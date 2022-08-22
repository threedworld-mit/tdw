from typing import Dict, List
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject
from tdw.controller import Controller


class Plate(ArrangementWithRootObject):
    """
    A kitchen plate that may have food on it.

    - The plate model is chosen randomly; see `TableSetting.MODEL_CATEGORIES["plate"]`.
    - The plate might have food on it; see `Plate.FOOD_PROBABILITY`.
      - The possible food categories are `Plate.FOOD_CATEGORIES`.
      - See `Plate.MODEL_CATEGORIES` for a list of models within those categories.
      - The position of the food is perturbed randomly.
      - The rotation of the food is random.
    """

    """:class_var
    The categories of possible food models.
    """
    FOOD_CATEGORIES: List[str] = ["apple", "banana", "chocolate", "orange", "sandwich"]
    """:class_var
    The probability from 0 to 1 of adding a food model on top of the plate.
    """
    FOOD_PROBABILITY: float = 0.8

    def get_commands(self) -> List[dict]:
        """
        :return: A list of commands that will generate the arrangement.
        """

        commands = self._add_root_object()
        if self._rng.random() < Plate.FOOD_PROBABILITY:
            extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
            food_category: str = Plate.FOOD_CATEGORIES[self._rng.randint(0, len(Plate.FOOD_CATEGORIES))]
            food = Plate.MODEL_CATEGORIES[food_category]
            food_model_name = food[self._rng.randint(0, len(food))]
            food_id = Controller.get_unique_id()
            self.object_ids.append(food_id)
            commands.extend(Controller.get_add_physics_object(model_name=food_model_name,
                                                              object_id=food_id,
                                                              position={"x": self._position["x"],
                                                                        "y": self._position["y"] + extents[1],
                                                                        "z": self._position["z"]},
                                                              rotation={"x": 0,
                                                                        "y": self._rng.uniform(0, 360),
                                                                        "z": 0},
                                                              library="models_core.json"))
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        return position

    def _get_rotation(self) -> float:
        return 0

    def _get_category(self) -> str:
        return "plate"
