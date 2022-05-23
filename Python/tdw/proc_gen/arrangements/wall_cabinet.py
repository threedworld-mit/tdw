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
      - Sometimes, there is a [`StackOfPlates`](stack_of_plates.md); see `WallCabinet.PROBABILITY_STACK_OF_PLATES`.
      - Sometimes, there is a rectangular arrangement of random objects; see `WallCabinet.PROBABILITY_CUPS`.
        - The objects are chosen randomly; see `WallCabinet.ENCLOSED_BY["wall_cabinet"]`.
        - The objects are positioned in a rectangular grid inside the wall cabinet with random rotations and positional perturbations; see `WallCabinet.CELL_SIZE`, `WallCabinet.CELL_DENSITY`, `WallCabinet.WIDTH_SCALE`, and `WallCabinet.DEPTH_SCALE`.
    - The root object of the wall cabinet is kinematic and the door sub-objects are non-kinematic.
    """

    """:class_var
    The value of the y positional coordinate (the height) of the wall cabinet.
    """
    Y: float = 1.289581
    """:class_var
    The probability between 0 and 1 of adding a [`StackOfPlates`](stack_of_plates.md).
    """
    PROBABILITY_STACK_OF_PLATES: float = 0.33
    """:class_var
    The probability between 0 and 1 of adding a rectangular arrangment of cups and glasses.
    """
    PROBABILITY_CUPS: float = 0.66
    """:class_var
    The probability from 0 to 1 of a "cell" in the cabinet rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    CELL_DENSITY: float = 0.1
    """:class_var
    The size of each cell in the cabinet rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    CELL_SIZE: float = 0.04
    """:class_var
    When adding objects, the width of the cabinet is assumed to be `actual_width * CABINET_WIDTH_SCALE`. This prevents objects from being too close to the edges of the cabinet.
    """
    WIDTH_SCALE: float = 0.8
    """:class_var
    When adding objects, the depth of the cabinet is assumed to be `actual_width * CABINET_DEPTH_SCALE`. This prevents objects from being too close to the edges of the cabinet.
    """
    DEPTH_SCALE: float = 0.8

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
            stack_of_plates = StackOfPlates(position=position,
                                            rng=self._rng)
            commands.extend(stack_of_plates.get_commands())
            self.object_ids.extend(stack_of_plates.object_ids)
        # Add a rectangular arrangement.
        else:
            if roll < WallCabinet.PROBABILITY_CUPS:
                categories = ["cup", "wineglass"]
            else:
                categories = WallCabinet.ENCLOSED_BY["wall_cabinet"]
            cmds, ids = self._add_rectangular_arrangement(size=(size["x"] * WallCabinet.WIDTH_SCALE,
                                                                size["z"] * WallCabinet.DEPTH_SCALE),
                                                          density=WallCabinet.CELL_DENSITY,
                                                          cell_size=WallCabinet.CELL_SIZE,
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
