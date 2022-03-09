from tdw.output_data import TriggerCollision


class TriggerCollisionEvent:
    """
    Data for a trigger collision event.
    """

    def __init__(self, collision: TriggerCollision):
        """
        :param collision: The [`TriggerCollision`](../../api/output_data.md#TriggerCollision) output data.
        """

        """:field
        The ID of the trigger collider.
        """
        self.trigger_id: int = collision.get_trigger_id()
        """:field
        The ID of the collidee object (the object that has the trigger collider).
        """
        self.collidee_id: int = collision.get_collidee_id()
        """:field
        The ID of the collider object (the object the collided with the trigger collider).
        """
        self.collider_id: int = collision.get_collider_id()
        """:field
        The state of the collision.
        """
        self.state: str = collision.get_state()
