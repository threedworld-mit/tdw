# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.robot_command import RobotCommand


class SetImmovable(RobotCommand):
    """
    Set whether or not the root object of the robot is immovable. Its joints will still be movable.
    """

    def __init__(self, immovable: bool = True, id: int = 0):
        """
        :param immovable: If true, the root object of the robot is immovable.
        :param id: The ID of the robot in the scene.
        """

        super().__init__(id=id)
        """:field
        If true, the root object of the robot is immovable.
        """
        self.immovable: bool = immovable
