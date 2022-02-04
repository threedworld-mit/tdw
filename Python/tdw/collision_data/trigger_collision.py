from tdw.output_data import TriggerCollision as Trigger


class TriggerCollision:
    """
    Data for a trigger collision event.
    """

    def __init__(self, collision: Trigger):
        """
        :param collision: The trigger collision output data.
        """

        """:field
        The ID of the trigger collider.
        """
        self.trigger_collider_id: int = collision.get_trigger_id()
        """:field
        The state of the collision.
        """
        self.state: str = collision.get_state()
