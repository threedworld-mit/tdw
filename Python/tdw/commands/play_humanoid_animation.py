# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.humanoid_command import HumanoidCommand


class PlayHumanoidAnimation(HumanoidCommand):
    """
    Play a motion capture animation on a humanoid. The animation must already be in memory via the add_humanoid_animation command.
    """

    def __init__(self, id: int, name: str, framerate: int = -1, forward: bool = True):
        """
        :param id: The unique object ID.
        :param name: The name of the animation clip to play.
        :param framerate: If greater than zero, play the animation at this framerate instead of the animation's framerate.
        :param forward: If True, play the animation normally. If False, play the naimation in reverse.
        """

        super().__init__(id=id)
        """:field
        The name of the animation clip to play.
        """
        self.name: str = name
        """:field
        If greater than zero, play the animation at this framerate instead of the animation's framerate.
        """
        self.framerate: int = framerate
        """:field
        If True, play the animation normally. If False, play the naimation in reverse.
        """
        self.forward: bool = forward