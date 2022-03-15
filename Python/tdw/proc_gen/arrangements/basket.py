from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Basket(ArrangementAlongWall):
    """
    A basket with random objects.

    - The basket model is chosen random; see `Basket.MODEL_CATEGORIES["basket"]`.
    - There are a random number of objects in the basket; see `BASKET.MIN_NUM_OBJECTS` and `BASKET.MAX_NUM_OBJECTS`.
      - The objects are chosen randomly; see `Basket.INSIDE_OF["basket"]`.
      - The rotations of the objects are random.
      - The starting positions of the objects are random, but they are placed at (x, z) coordinates within the basket and at a y coordinate _above_ the basket. Each y coordinate is higher than the other to prevent interpenetration; see `Basket.DELTA_Y`.
    - The basket is placed next to a wall at a random distance offset: `extent * random.uniform(Basket.MIN_DEPTH_OFFSET, Basket.MAX_DEPTH_OFFSET)`.
    - The basket is rotated randomly; see `Basket.ROTATION`.
    """

    """:class_var
    The minimum number of objects in a basket.
    """
    MIN_NUM_OBJECTS: int = 2
    """:class_var
    The maximum number of objects in a basket.
    """
    MAX_NUM_OBJECTS: int = 2
    """:class_var
    The minimum offset from the wall.
    """
    MIN_DEPTH_OFFSET: float = 1.15
    """:class_var
    The maximum offset from the wall.
    """
    MAX_DEPTH_OFFSET: float = 1.25
    """:class_var
    Add this length to the basket's length when creating lateral arrangements.
    """
    LENGTH_OFFSET: float = 0.1
    """:class_var
    Baskets are randomly rotated up to +/- this many degrees.
    """
    ROTATION: float = 10
    """:class_var
    Each subsequent object in the basket is placed this many meters above the previous.
    """
    DELTA_Y: float = 0.25
    
    def get_commands(self) -> List[dict]:
        commands = self._add_root_object(kinematic=False)
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        d = extents[0] if extents[0] < extents[2] else extents[2]
        d *= 0.6
        r = d / 2
        y = extents[1]
        for i in range(self._rng.randint(Basket.MIN_NUM_OBJECTS, Basket.MAX_NUM_OBJECTS + 1)):
            category = Basket.INSIDE_OF["basket"][self._rng.randint(0, len(Basket.INSIDE_OF["basket"]))]
            model_name = Basket.MODEL_CATEGORIES[category][self._rng.randint(0, len(Basket.MODEL_CATEGORIES[category]))]
            q = TDWUtils.get_random_point_in_circle(center=np.array([self._position["x"], y, self._position["z"]]),
                                                    radius=r)
            q[1] = y
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              object_id=Controller.get_unique_id(),
                                                              position=TDWUtils.array_to_vector3(q),
                                                              rotation={"x": float(self._rng.uniform(0, 360)),
                                                                        "y": float(self._rng.uniform(0, 360)),
                                                                        "z": float(self._rng.uniform(0, 360))},
                                                              library="models_core.json"))
            y += Basket.DELTA_Y
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] + Basket.LENGTH_OFFSET

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2] * self._rng.uniform(Basket.MIN_DEPTH_OFFSET,
                                                                                              Basket.MAX_DEPTH_OFFSET)

    def _get_rotation(self) -> float:
        return float(self._rng.uniform(-Basket.ROTATION, Basket.ROTATION))

    def _get_category(self) -> str:
        return "basket"
