# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_type_command import ObjectTypeCommand
from typing import Dict


class SetColorInSubstructure(ObjectTypeCommand):
    """
    Set the color of a specific child object in the model's substructure. See: ModelRecord.substructure in the ModelLibrarian API.
    """

    def __init__(self, id: int, object_name: str, color: Dict[str, float]):
        """
        :param id: The unique object ID.
        :param object_name: The name of the sub-object.
        :param color: Set the object to this color.
        """

        super().__init__(id=id)
        """:field
        Set the object to this color.
        """
        self.color: Dict[str, float] = color
        """:field
        The name of the sub-object.
        """
        self.object_name: str = object_name