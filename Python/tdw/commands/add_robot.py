# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.add_object_command import AddObjectCommand
from typing import Dict


class AddRobot(AddObjectCommand):
    """
    Add a robot to the scene. For further documentation, see: Documentation/lessons/robots/overview.md
    """

    def __init__(self, url: str, name: str, id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None):
        """
        :param url: The location of the asset bundle. If the asset bundle is remote, this must be a valid URL. If the asset is a local file, this must begin with the prefix "file:///"
        :param name: The name of the asset bundle.
        :param id: The unique ID of the robot.
        :param position: The initial position of the robot.
        :param rotation: The initial rotation of the robot in Euler angles.
        """

        super().__init__(name=name, url=url)
        """:field
        The unique ID of the robot.
        """
        self.id: int = id
        if position is None:
            """:field
            The initial position of the robot.
            """
            self.position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.position = position
        if rotation is None:
            """:field
            The initial rotation of the robot in Euler angles.
            """
            self.rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.rotation = rotation