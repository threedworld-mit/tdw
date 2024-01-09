# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.robot_command import RobotCommand


class MakeRobotNavMeshObstacle(RobotCommand):
    """
    Make a specific robot a NavMesh obstacle. If it is already a NavMesh obstacle, change its properties.
    """

    def __init__(self, carve_type: str = "all", scale: float = 1, shape: str = "box", id: int = 0):
        """
        :param carve_type: How the robot will "carve" holes in the NavMesh.
        :param scale: The scale of the obstacle relative to the size of the robot. Set this lower to account for the additional space that the robot will carve.
        :param shape: The shape of the carver.
        :param id: The ID of the robot in the scene.
        """

        super().__init__(id=id)
        """:field
        How the robot will "carve" holes in the NavMesh.
        """
        self.carve_type: str = carve_type
        """:field
        The scale of the obstacle relative to the size of the robot. Set this lower to account for the additional space that the robot will carve.
        """
        self.scale: float = scale
        """:field
        The shape of the carver.
        """
        self.shape: str = shape