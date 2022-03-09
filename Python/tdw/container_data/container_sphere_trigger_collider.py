from typing import Dict
from tdw.container_data.container_collider_tag import ContainerColliderTag
from tdw.container_data.container_trigger_collider import ContainerTriggerCollider
from tdw.collision_data.trigger_collider_shape import TriggerColliderShape


class ContainerSphereTriggerCollider(ContainerTriggerCollider):
    """
    Data for a container trigger sphere collider.
    """

    def __init__(self, tag: ContainerColliderTag, position: Dict[str, float], diameter: float):
        """
        :param tag: The collider's semantic [`ContainerColliderTag`](container_collider_tag.md).
        :param position: The local position of the collider.
        :param diameter: The diameter of the collider.
        """

        """:field
        The diameter of the collider.
        """
        self.diameter: float = diameter
        super().__init__(tag=tag, position=position)

    def _get_shape(self) -> TriggerColliderShape:
        return TriggerColliderShape.sphere

    def _get_bottom_y(self) -> float:
        return self.position["y"] - self.diameter / 2
