# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_data_command import SendDataCommand


class SendStaticRobots(SendDataCommand):
    """
    Send static data that doesn't update per frame (such as segmentation colors) for each robot in the scene. See also: send_robots
    """

    def __init__(self, frequency: str = "once"):
        """
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(frequency=frequency)
