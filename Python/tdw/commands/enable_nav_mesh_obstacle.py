# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_command import ObjectCommand


class EnableNavMeshObstacle(ObjectCommand):
    """
    Enable or disable an object's NavMeshObstacle. If the object doesn't have a NavMeshObstacle, this command does nothing.
    """

    def __init__(self, id: int, enable: bool):
        """
        :param id: The unique object ID.
        :param enable: If True, enable the NavMeshObstacle. If False, disable the NavMeshObstacle.
        """

        super().__init__(id=id)
        """:field
        If True, enable the NavMeshObstacle. If False, disable the NavMeshObstacle.
        """
        self.enable: bool = enable