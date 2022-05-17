from typing import Dict, List, Union
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement import Arrangement
from tdw.controller import Controller


class StackOfPlates(Arrangement):
    """
    A stack of plates.

    - The plate model is chosen randomly and is the same for each plate; see `StackOfPlates.MODEL_CATEGORIES["plate"]`.
    - The number of plates in the stack is random; see `min_num` and `max_num` in the constructor.
    """

    def __init__(self, min_num: int, max_num: int, position: Dict[str, float], rng: Union[int, np.random.RandomState] = None):
        """
        :param min_num: The minimum number of plates.
        :param max_num: The maximum number of plates.
        :param position: The position of the root object. This might be adjusted.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        super().__init__(position=position, rng=rng)
        self._num_plates: int = self._rng.randint(min_num, max_num + 1)

    def get_commands(self) -> List[dict]:
        model_name = Arrangement.MODEL_CATEGORIES["plate"][self._rng.randint(0, len(Arrangement.MODEL_CATEGORIES["plate"]))]
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        y = self._position["y"]
        commands = []
        for i in range(self._num_plates):
            object_id = Controller.get_unique_id()
            self.object_ids.append(object_id)
            commands.extend(Controller.get_add_physics_object(model_name=model_name,
                                                              object_id=object_id,
                                                              position={"x": self._position["x"],
                                                                        "y": y,
                                                                        "z": self._position["z"]}))
            y += extents[1]
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        return position

    def _get_rotation(self) -> float:
        return 0
