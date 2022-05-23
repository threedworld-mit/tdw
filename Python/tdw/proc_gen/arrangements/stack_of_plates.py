from typing import Dict, List
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement import Arrangement
from tdw.controller import Controller


class StackOfPlates(Arrangement):
    """
    A stack of plates.

    - The plate model is chosen randomly and is the same for each plate; see `StackOfPlates.MODEL_CATEGORIES["plate"]`.
    - The number of plates in the stack is random; see `StackOfPlates.MIN_NUM` and `StackOfPlates.MAX_NUM`.
    """

    """:class_var
    The minimum number of plates in a stack of plates.
    """
    MIN_NUM: int = 3
    """:class_var
    The maximum number of plates in a stack of plates.
    """
    MAX_NUM: int = 8

    def get_commands(self) -> List[dict]:
        model_name = Arrangement.MODEL_CATEGORIES["plate"][self._rng.randint(0, len(Arrangement.MODEL_CATEGORIES["plate"]))]
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        y = self._position["y"]
        commands = []
        num_plates = self._rng.randint(StackOfPlates.MIN_NUM, StackOfPlates.MAX_NUM + 1)
        for i in range(num_plates):
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
