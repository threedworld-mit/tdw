from tdw.collision_data.trigger_collider_shape import TriggerColliderShape
from tdw.container_data.container_non_uniform_scale_trigger_collider import ContainerNonUniformScaleTriggerCollider


class ContainerBoxTriggerCollider(ContainerNonUniformScaleTriggerCollider):
    """
    Data for a container trigger box collider.
    """

    def _get_shape(self) -> TriggerColliderShape:
        return TriggerColliderShape.box
