# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.object_command import ObjectCommand


class FlexObjectCommand(ObjectCommand, ABC):
    """
    These commands apply only to objects that already have FlexActor components.
    """

    def __init__(self, id: int):
        """
        :param id: The unique object ID.
        """

        super().__init__(id=id)
