from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects_data.arrangement_with_root_object import ArrangementWithRootObject
from tdw.librarian import ModelRecord
from tdw.controller import Controller


class Plate(ArrangementWithRootObject):
    """
    A kitchen plate may have food on top of it; see `food_probability` in the constructor.

    The possible food categories are `Plate.FOOD_CATEGORIES`; see `Plate.MODEL_CATEGORIES` for a list of models within those categories.

    The plate model is chosen randomly; see `Plate.MODEL_CATEGORIES["plate"]`.
    """

    """:class_var
    The categories of possible food models.
    """
    FOOD_CATEGORIES: List[str] = ["apple", "banana", "chocolate", "orange", "sandwich"]

    def __init__(self, food_probability: float, record: ModelRecord, position: Dict[str, float], rng: np.random.RandomState):
        """
        :param food_probability: The probability of placing food on the plate.
        :param record: The record of the root object.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        self._food_probability: float = food_probability
        super().__init__(record=record, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        """
        :return: A list of commands that will generate the arrangement.
        """

        plate_id, commands = self._add_root_object()
        if self._rng.random() < self._food_probability:
            extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
            food_category: str = Plate.FOOD_CATEGORIES[self._rng.randint(0, len(Plate.FOOD_CATEGORIES))]
            food = Plate.MODEL_CATEGORIES[food_category]
            food_model_name = food[self._rng.randint(0, len(food))]
            food_id = Controller.get_unique_id()
            self.object_ids.append(food_id)
            commands.extend(Controller.get_add_physics_object(model_name=food_model_name,
                                                              object_id=food_id,
                                                              position={"x": self._position["x"] + self._rng.uniform(-0.03, 0.03),
                                                                        "y": self._position["y"] + extents[1],
                                                                        "z": self._position["z"] + self._rng.uniform(-0.03, 0.03)},
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
