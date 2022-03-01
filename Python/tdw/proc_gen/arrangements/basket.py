from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Basket(ArrangementAlongWall):
    """
    A basket with random objects.

    - The basket model is chosen random; see `Basket.MODEL_CATEGORIES["basket"]`.
    - There are 2-5 objects in the basket.
    - The objects in the basic are chosen randomly; see `Basket.INSIDE_OF["basket"]`.
    - The rotations of these objects are random.
    - The starting positions of the objects are random, but they are placed at (x, z) coordinates within the basket and at a y coordinate _above_ the basket. Each y coordinate is higher than the other; the change in height is random but is guaranteed to prevent interpenetration.
    - The basket is placed next to a wall at a random distance offset: `extent * random.uniform(1.15, 1.25)`.
    - The basket is rotated randomly between -10 and 10 degrees.
    - The basket object is non-kinematic.
    """
    
    def _get_commands(self) -> List[dict]:
        commands = self._add_root_object(kinematic=False)
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        d = extents[0] if extents[0] < extents[2] else extents[2]
        d *= 0.6
        r = d / 2
        y = extents[1]
        for i in range(self._rng.randint(2, 6)):
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
            y += 0.25
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] + 0.05

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2] * self._rng.uniform(1.15, 1.25)

    def _get_rotation(self) -> float:
        return float(self._rng.uniform(-10, 10))

    def _get_category(self) -> str:
        return "basket"
