# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.obi_actor_command import ObiActorCommand
from typing import Dict


class RotateObiActorTo(ObiActorCommand):
    """
    Set an Obi actor's rotation.
    """

    def __init__(self, id: int, rotation: Dict[str, float]):
        """
        :param id: The unique object ID.
        :param rotation: The rotation.
        """

        super().__init__(id=id)
        """:field
        The rotation.
        """
        self.rotation: Dict[str, float] = rotation