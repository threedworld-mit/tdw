from typing import Dict, List
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet


class WallCabinet(KitchenCabinet):
    """
    A wall cabinet hangs on the wall above a kitchen counter.
    """

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        pos["y"] = 1.289581
        return pos

    def _get_category(self) -> str:
        return "wall_cabinet"
