from typing import List, Dict
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.plate import Plate
from tdw.proc_gen.arrangements.cup_and_coaster import CupAndCoaster


class TableSetting(Plate):
    """
    A table setting includes a plate, fork, knife, spoon, and sometimes a cup.

    - This is a subclass of [`Plate`](plate.md).
    - The fork, knife, and spoon models are random; see `TableSetting.MODEL_CATEGORIES["fork"]`, `TableSetting.MODEL_CATEGORIES["knife"]`, and `TableSetting.MODEL_CATEGORIES["spoon"]`.
      - The rotations of the fork, knife, and spoon are perturbed randomly (-3 to 3 degrees).
      - The positions of the fork, knife, and spoon are perturbed randomly (0.03 to 0.05 meters).
    - 66% of the time, there is a [`CupAndCoaster`](cup_and_coaster.md).
    """

    def __init__(self, food_probability: float, position: Dict[str, float], rng: np.random.RandomState):
        """
        :param food_probability: The probability of placing food on the plate.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        super().__init__(food_probability=food_probability, model="plate06", position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = super().get_commands()
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        fork_x = self._position["x"] - (extents[0] / 2 + self._rng.uniform(0.03, 0.05))
        knife_x = self._position["x"] + extents[0] / 2 + self._rng.uniform(0.03, 0.05)
        spoon_x = knife_x + self._rng.uniform(0.03, 0.07)
        for category, x in zip(["fork", "knife", "spoon"], [fork_x, knife_x, spoon_x]):
            model_name = TableSetting.MODEL_CATEGORIES[category][self._rng.randint(0, len(TableSetting.MODEL_CATEGORIES[category]))]
            object_id = Controller.get_unique_id()
            self.object_ids.append(object_id)
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              object_id=object_id,
                                                              position={"x": x,
                                                                        "y": self._position["y"],
                                                                        "z": self._position["z"] + self._rng.uniform(-0.03, 0.03)},
                                                              rotation={"x": 0,
                                                                        "y": float(self._rng.uniform(-3, 3)),
                                                                        "z": 0},
                                                              library="models_core.json"))
        # Add a cup.
        if self._rng.random() > 0.33:
            cup_and_coaster = CupAndCoaster(position={"x": spoon_x + self._rng.uniform(-0.05, 0.01),
                                                      "y": self._position["y"],
                                                      "z": self._position["z"] + extents[2] / 2 + self._rng.uniform(0.06, 0.09)},
                                            rng=self._rng)
            commands.extend(cup_and_coaster.get_commands())
            self.object_ids.extend(cup_and_coaster.object_ids)
        return commands
