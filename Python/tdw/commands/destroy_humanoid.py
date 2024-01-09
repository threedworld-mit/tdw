# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.humanoid_command import HumanoidCommand


class DestroyHumanoid(HumanoidCommand):
    """
    Destroy a humanoid.
    """

    def __init__(self, id: int):
        """
        :param id: The unique object ID.
        """

        super().__init__(id=id)
