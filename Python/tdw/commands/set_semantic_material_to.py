# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_type_command import ObjectTypeCommand


class SetSemanticMaterialTo(ObjectTypeCommand):
    """
    Sets or creates the semantic material category of an object.
    """

    def __init__(self, id: int, material_type: str):
        """
        :param id: The unique object ID.
        :param material_type: The semantic material type.
        """

        super().__init__(id=id)
        """:field
        The semantic material type.
        """
        self.material_type: str = material_type
