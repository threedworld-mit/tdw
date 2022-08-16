from typing import List, Union, Dict
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms
from tdw.replicant.affordance_points import AffordancePoints
import numpy as np

class ReplicantUtils():

    @staticmethod
    def get_object_position(resp: List[bytes], object_id: int):
        for i in range(len(resp) - 1):
            # Get the output data ID.
            r_id = OutputData.get_data_type_id(resp[i])
            # This is transforms output data.
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == object_id:
                        return TDWUtils.array_to_vector3(transforms.get_position(j))


    @staticmethod
    def get_add_object_with_affordance_points(model_name: str, object_id: int, position: Dict[str, float] = None,
                                              rotation: Dict[str, float] = None, library: str = "",
                                              scale_factor: Dict[str, float] = None, kinematic: bool = False,
                                              gravity: bool = True,
                                              default_physics_values: bool = True, mass: float = 1,
                                              dynamic_friction: float = 0.3,
                                              static_friction: float = 0.3, bounciness: float = 0.7) -> List[dict]:
        # Add the object with physics parameters.
        commands = Controller.get_add_physics_object(model_name=model_name, object_id=object_id, position=position,
                                                     rotation=rotation, library=library, scale_factor=scale_factor,
                                                     kinematic=kinematic, gravity=gravity,
                                                     default_physics_values=default_physics_values, mass=mass,
                                                     dynamic_friction=dynamic_friction, static_friction=static_friction,
                                                     bounciness=bounciness)
        # Add affordance points.
        if model_name in AffordancePoints.AFFORDANCE_POINTS:
            for affordance_position in AffordancePoints.AFFORDANCE_POINTS[model_name]:
                # Remember the original local positions.
                AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id] = dict()
                empty_object_id = Controller.get_unique_id()
                # Cache the mapping between empty object IDs and the ID of the parent object.
                AffordancePoints.EMPTY_OBJECT_IDS[empty_object_id] = {"object_id": object_id,
                                                                             "position": affordance_position}
                # Add a command to attach an empty object.
                commands.extend([{"$type": "attach_empty_object",
                                 "id": object_id,
                                 "empty_object_id": empty_object_id,
                                 "position": affordance_position},
                                 {"$type": "add_position_marker", 
                                  "position":  {'x': affordance_position['x'], 'y': affordance_position['y'] + 0.35, 'z': affordance_position['z']}, 
                                  "scale": 0.05, 
                                  "color": {"r": 1, "g": 0, "b": 0, "a": 1},
                                  "shape": "sphere"}])
                # Remember the position.
                AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id][empty_object_id] = affordance_position
        return commands

    @staticmethod
    def get_direction(self, forward: np.array, origin: np.array, target: np.array) -> bool:
        """
        :param forward: The forward directional vector.
        :param origin: The origin position.
        :param target: The target position.

        :return: True if the target is to the left of the origin by the forward vector; False if it's to the right.
        """
        # Get the heading.
        target_direction = target - origin
        # Normalize the heading.
        #target_direction = target_direction / np.linalg.norm(target_direction)
        perpendicular: np.array = np.cross(forward, target_direction)
        direction = np.dot(perpendicular, QuaternionUtils.UP)
        return direction

