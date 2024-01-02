# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.object_type_command import ObjectTypeCommand


class VisualMaterialCommand(ObjectTypeCommand, ABC):
    """
    Commands that involve the visual material(s) of an object. See MongoDBRecord.ObjectMaterialData for data of the object's hierarchical substructure.
    """

    def __init__(self, id: int, object_name: str):
        """
        :param id: The unique object ID.
        :param object_name: The name of the sub-object.
        """

        super().__init__(id=id)
        """:field
        The name of the sub-object.
        """
        self.object_name: str = object_name
