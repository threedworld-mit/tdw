from typing import Dict, List, Optional
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.box_container import BoxContainer
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet
from tdw.proc_gen.arrangements.stack_of_plates import StackOfPlates


class WallCabinet(KitchenCabinet):
    """
    A wall cabinet hangs on the wall above a kitchen counter. It can have objects inside it.

    - The wall cabinet model is chosen randomly; see `WallCabinet.MODEL_CATEGORIES["wall_cabinet"]`.
    - The wall cabinet is placed next to a wall.
      - The wall cabinet's position is automatically adjusted to set it flush to the wall.
      - The wall cabinet is automatically rotated so that it faces away from the wall.
      - The wall cabinet is at a fixed height from the wall, see `WALL_CABINET.Y`.
    - The wall cabinet always has objects inside it. The contents are random:
      - Sometimes, there is a [`StackOfPlates`](stack_of_plates.md); see `WallCabinet.PROBABILITY_STACK_OF_PLATES`, `WallCabinet.MIN_NUM_PLATES`, and `WallCabinet.MAX_NUM_PLATES`.
      - Sometimes, there is a rectangular arrangement of random objects; see `WallCabinet.PROBABILITY_CUPS`.
        - The objects are chosen randomly; see `WallCabinet.ENCLOSED_BY["wall_cabinet"]`.
        - The objects are positioned in a rectangular grid inside the wall cabinet with random positional perturbations.
        - The objects have random rotations (0 to 360 degrees).
    - The root object of the wall cabinet is kinematic and the door sub-objects are non-kinematic.
    """

    """:class_var
    The value of the y positional coordinate (the height) of the wall cabinet.
    """
    Y: float = 1.289581
    """:class_var
    To decide what is within the cabinet, a random number between 0 and 1 is generated. If the number is below this value, a [`StackOfPlates`](stack_of_plates.md) is added.
    """
    PROBABILITY_STACK_OF_PLATES: float = 0.33
    """:class_var
    To decide what is within the cabinet, a random number between 0 and 1 is generated. If the number is below this value, a rectangular arrangement of cups and glasses is added. If the number is above this value, random objects are added (see `WallCabinet.ENCLOSED_BY["wall_cabinet"]`).
    """
    PROBABILITY_CUPS: float = 0.66
    """:class_var
    The minimum number of plates in a stack of plates.
    """
    MIN_NUM_PLATES: int = 3
    """:class_var
    The maximum number of plates in a stack of plates.
    """
    MAX_NUM_PLATES: int = 8

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        # Get the bottom-center position of the inner cavity.
        cabinet_shape: Optional[BoxContainer] = None
        for shape in self._record.container_shapes:
            if shape.tag == ContainerTag.enclosed and isinstance(shape, BoxContainer):
                cabinet_shape = shape
                break
        position, size = self._get_container_shape_position_and_size(shape=cabinet_shape)
        roll = self._rng.random()
        # Add a stack of plates.
        if roll < WallCabinet.PROBABILITY_STACK_OF_PLATES:
            stack_of_plates = StackOfPlates(min_num=WallCabinet.MIN_NUM_PLATES,
                                            max_num=WallCabinet.MAX_NUM_PLATES,
                                            position=position,
                                            rng=self._rng)
            commands.extend(stack_of_plates.get_commands())
            self.object_ids.extend(stack_of_plates.object_ids)
        # Add a rectangular arrangement.
        else:
            if roll < WallCabinet.PROBABILITY_CUPS:
                categories = ["cup", "wineglass"]
            else:
                categories = WallCabinet.ENCLOSED_BY["wall_cabinet"]
            cmds, ids = self._add_rectangular_arrangement(size=(size["x"] * 0.8, size["z"] * 0.8),
                                                          position=position,
                                                          categories=categories)
            commands.extend(cmds)
            self.object_ids.extend(ids)
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        pos["y"] = WallCabinet.Y
        return pos

    def _get_category(self) -> str:
        return "wall_cabinet"

    def _get_model_names(self) -> List[str]:
        return self._cabinetry.wall_cabinets