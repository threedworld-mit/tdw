# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.command import Command


class SetTimeStep(Command):
    """
    Set Time.fixedDeltaTime (Unity's physics step, as opposed to render time step). NOTE: Doubling the time_step is NOT equivalent to advancing two physics steps. For more information, see: [https://docs.unity3d.com/Manual/TimeFrameManagement.html](https://docs.unity3d.com/Manual/TimeFrameManagement.html)
    """

    def __init__(self, time_step: float = 0.01):
        """
        :param time_step: Time.fixedDeltaTime
        """

        super().__init__()
        """:field
        Time.fixedDeltaTime
        """
        self.time_step: float = time_step
