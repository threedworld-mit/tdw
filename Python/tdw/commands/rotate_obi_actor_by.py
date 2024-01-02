# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.obi_actor_command import ObiActorCommand


class RotateObiActorBy(ObiActorCommand):
    """
    Rotate an Obi actor by a given angle around a given axis.
    """

    def __init__(self, id: int, angle: float, axis: str = "yaw", is_world: bool = True):
        """
        :param id: The unique object ID.
        :param angle: The angle of rotation in degrees.
        :param axis: The axis of rotation.
        :param is_world: If True, the object will rotate around global axes. If False, the object will around local axes. Ignored if use_centroid == False.
        """

        super().__init__(id=id)
        """:field
        The axis of rotation.
        """
        self.axis: str = axis
        """:field
        The angle of rotation in degrees.
        """
        self.angle: float = angle
        """:field
        If True, the object will rotate around global axes. If False, the object will around local axes. Ignored if use_centroid == False.
        """
        self.is_world: bool = is_world
