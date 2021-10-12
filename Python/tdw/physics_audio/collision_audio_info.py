from tdw.physics_audio.modes import Modes


class CollisionAudioInfo:
    """
    Class containing information about collisions required by PyImpact to determine the volume of impact sounds.
    """

    def __init__(self, obj1_modes: Modes, obj2_modes: Modes, amp: float = 0.5, init_speed: float = 1):
        """
        :param amp: Amplitude of the first collision (must be between 0 and 1).
        :param init_speed: The speed of the initial collision (all collisions will be scaled relative to this).
        :param obj1_modes: The object's modes.
        :param obj2_modes: The other object's modes.
        """

        """:field
        The collision counter.
        """
        self.count: int = 0
        """:field
        Amplitude of the first collision (must be between 0 and 1).
        """
        self.amp: float = amp
        """:field
        The speed of the initial collision.
        """
        self.init_speed: float = init_speed
        """:field
        The object's modes.
        """
        self.obj1_modes: Modes = obj1_modes
        """:field
        The other object's modes.
        """
        self.obj2_modes: Modes = obj2_modes

    def count_collisions(self) -> None:
        """
        Update the counter for how many times two objects have collided.
        """

        self.count += 1
