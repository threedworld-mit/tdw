from typing import Dict, List, Optional
from tdw.container_data.container_collider_tag import ContainerColliderTag
from tdw.container_data.container_box_trigger_collider import ContainerBoxTriggerCollider
from tdw.proc_gen.arrangements.kitchen_cabinet import KitchenCabinet
from tdw.proc_gen.arrangements.stack_of_plates import StackOfPlates


class WallCabinet(KitchenCabinet):
    """
    A wall cabinet hangs on the wall above a kitchen counter. It can have objects inside it.

    - The wall cabinet model is chosen randomly; see `WallCabinet.MODEL_CATEGORIES["wall_cabinet"]`.
    - The wall cabinet is placed next to a wall.
      - The wall cabinet's position is automatically adjusted to set it flush to the way.
      - The wall cabinet is automatically rotated so that it faces away from the wall.
    - The wall cabinet always has objects inside of it. The contents are random:
      - 33% of the time, there is a [`StackOfPlates`](stack_of_plates.md).
      - 66% of the time, there is a rectangular arrangement of random objects:
        - 33% of the time, the categories are: `["cup", "wineglass"]`.
        - 33% of the time, the categories are: `["bowl", "bottle", "cup", "jar", "jug", "vase", "wineglass"]`
    - The root object of the wall cabinet is kinematic and the door sub-objects are non-kinematic.
    """

    def _get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        # Get the bottom-center position of the inner cavity.
        cabinet_collider: Optional[ContainerBoxTriggerCollider] = None
        for collider in self._record.container_colliders:
            if collider.tag == ContainerColliderTag.enclosed and isinstance(collider, ContainerBoxTriggerCollider):
                cabinet_collider = collider
                break
        position = self._get_collider_position(collider=cabinet_collider)
        roll = self._rng.random()
        # Add a stack of plates.
        if roll < 0.33:
            stack_of_plates = StackOfPlates(min_num=3, max_num=8, position=position, rng=self._rng)
            commands.extend(stack_of_plates.get_commands())
            self.object_ids.extend(stack_of_plates.object_ids)
        # Add a rectangular arrangement.
        else:
            if roll < 0.66:
                categories = ["cup", "wineglass"]
            else:
                categories = WallCabinet.ENCLOSED_BY["wall_cabinet"]
            cmds, ids = self._add_rectangular_arrangement(size=(cabinet_collider.scale["x"] * 0.8,
                                                                cabinet_collider.scale["z"] * 0.8),
                                                          position=position,
                                                          categories=categories)
            commands.extend(cmds)
            self.object_ids.extend(ids)
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        pos["y"] = 1.289581
        return pos

    def _get_category(self) -> str:
        return "wall_cabinet"

    def _get_model_names(self) -> List[str]:
        return KitchenCabinet._CABINETRY.wall_cabinets
