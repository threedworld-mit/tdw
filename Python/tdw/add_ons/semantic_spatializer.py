from os import urandom
from typing import Dict, Union, Tuple
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager


class SemanticSpatializer(ObjectManager):
    """
    Position objects *that are already in the scene* with spatial semantics, e.g. to the left or right of a position or object.
    """
    
    def __init__(self, random_seed: int = None):
        """
        :param random_seed: The random seed. This is used to set random distances, angles, etc. If None, the seed is random.
        """

        super().__init__(transforms=True, rigidbodies=True, bounds=True)
        if random_seed is None:
            """:field
            The random seed. This is used to set random distances, angles, etc. If None, the seed is random
            """
            self.random_seed: int = int.from_bytes(urandom(3), byteorder='big')
        else:
            self.random_seed = random_seed
        """:field
        The random number generator.
        """
        self.rng: np.random.RandomState = np.random.RandomState(self.random_seed)

    def left_right(self, object_id: int, relative_position: Union[Dict[str, float], np.ndarray, Tuple[int, str]],
                   angle_range: Tuple[float, float], xz_range: Tuple[float, float], y_range: Tuple[float, float],
                   is_left: bool, worldspace: bool = True) -> None:
        """
        Move an object to be left or right of another object or position. This will move the object on the next `communicate()` call.

        :param object_id: The ID of the object being moved.
        :param relative_position: The relative position. This can be: A dictionary representing a position e.g. {"x": 0, "y": 0, "z": 0}`, a numpy array representing a position e.g. `np.array([0, 0, 0])`, or a tuple where the first element is the object ID of a parent object and the second element is the name of a bound point e.g. `(1, "center")`.
        :param angle_range: A range of angles in degrees relative to the left or right directional vector.
        :param xz_range: A range of a distance in meters along the (x, z) plane.
        :param y_range: A range of a distance in meters along the y axis.
        :param is_left: If True, the object will be left of `relative_position`. If False, the object will be right of `relative_position`.
        :param worldspace: If `relative_position` is a tuple of `(object_id, bound_point)`, this parameter sets whether the left/right directional vector is the worldspace left/right directional vector (`True`) or the object's left/right directional vector (`False`).
        """

        # Get the point and the direction.
        point: np.ndarray
        direction: np.ndarray
        # These are flipped on purpose!
        if is_left:
            direction = TDWUtils.RIGHT
        else:
            direction = TDWUtils.LEFT
        # This is a position.
        if isinstance(relative_position, dict) or isinstance(relative_position, np.ndarray):
            # Convert a dictionary to a numpy array.
            if isinstance(relative_position, dict):
                point = TDWUtils.vector3_to_array(relative_position)
            # This is a numpy array position.
            elif isinstance(relative_position, np.ndarray):
                point = relative_position
            else:
                raise Exception(relative_position)
        # Get a points point.
        elif isinstance(relative_position, tuple):
            point = self.bounds[relative_position[0]].__dict__[relative_position[1]]
            # The forward directional vector is the object's forward.
            if not worldspace:
                forward = self.transforms[relative_position[0]].forward
                # Rotate left or right.
                if is_left:
                    direction = TDWUtils.get_rotated_vector(forward, 90)
                else:
                    direction = TDWUtils.get_rotated_vector(forward, -90)
        else:
            raise Exception(relative_position)
        # Get a random angle.
        angle = self.rng.uniform(angle_range[0], angle_range[1])
        # Get a random (x, z) distance.
        distance_xz = self.rng.uniform(xz_range[0], xz_range[1])
        # Rotate the direction by the angle.
        direction = TDWUtils.get_rotated_vector(direction, angle)
        # Get the (x, z) direction.
        direction_xz = np.array([direction[0], direction[2]])
        # Get the (x, z) position.
        xz = np.array([point[0], point[2]]) + direction_xz * distance_xz
        # Get a random y value.
        y = self.rng.uniform(y_range[0], y_range[1]) + point[1]
        # Get the position.
        xyz = np.array([xz[0], y, xz[1]])
        # Add the command.
        self.commands.append({"$type": "teleport_object",
                              "position": TDWUtils.array_to_vector3(xyz),
                              "id": object_id})
