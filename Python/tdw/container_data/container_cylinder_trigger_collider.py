from tdw.collision_data.trigger_collider_shape import TriggerColliderShape
from tdw.container_data.container_non_uniform_scale_trigger_collider import ContainerNonUniformScaleTriggerCollider


class ContainerCylinderTriggerCollider(ContainerNonUniformScaleTriggerCollider):
    """
    Data for a container trigger cylinder collider.
    """

    def _get_shape(self) -> TriggerColliderShape:
        return TriggerColliderShape.cylinder
