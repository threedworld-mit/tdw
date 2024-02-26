import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.enum_member import EnumMember
from tdw.dev.code_gen.cs_xml.enum_type import EnumType


class FieldDoc(ABC):
    """
    Documentation text for a field.
    """

    """:field
    Regex to find a field that is defining a name.
    """
    RE_NAME: re.Pattern = re.compile(r'\w+_name')
    """:field
    Use these example values for the documentation code examples. Key = The name of the field. Value = The code examples' example values. 
    """
    EXAMPLE_VALUES_BY_PARAMETER_NAME: Dict[str, str] = {'image': '"base64imagedata"',
                                                        'pass_masks': '["_img"]',
                                                        'text': '"string"',
                                                        'url': '"https://path/to/asset"',
                                                        'force': '1.25',
                                                        'angle': '-90.5',
                                                        'radius': '2.5',
                                                        'magnitude': '1.3',
                                                        'duration': '2',
                                                        'mass': '5.3'}

    def __init__(self, field: Field, enums: Dict[str, EnumType]):
        """
        :param field: A Field.
        :param enums: All EnumTypes in the assembly.
        """

        """:field
        The field's row in a table of fields.
        """
        self.row: str = f'| {self._get_name(field)} | {self._get_type(field, enums)} | {field.description} | '
        """:field
        If this field is an enum type, then this is a table of enum members. Otherwise, this is None.
        """
        self.enum_table: Optional[str] = None
        default_value: Optional[str] = self._get_default_value(field)
        # There is a default value. Use it!
        if default_value is not None:
            """:field
            The field's value as it will appear in a code example.
            """
            self.value: str = default_value
            # Add the default value to the row.
            self.row += f'{default_value} |'
            """:field
            If True, this field has a default value.
            """
            self.has_default: bool = True
        # There is no default value. The row won't include a value but we need a `self.value` for the example.
        else:
            self.row += '|'
            self.has_default = False
            # Set the default ID value.
            if field.name == 'id':
                if field.py_field_type == 'str':
                    self.value = '"a"'
                elif field.py_field_type == 'int':
                    self.value = '0'
                else:
                    raise Exception(f'Invalid id field type: {field.name} {field.py_field_type}')
            # Set the default list of IDs value.
            elif field.name == 'ids':
                if field.cs_field_type == 'str[]':
                    self.value = self._get_array('"a"')
                elif field.cs_field_type == 'int[]':
                    self.value = self._get_array('0')
                elif field.cs_field_type == 'byte[]':
                    self.value = self._get_array('0')
                elif field.cs_field_type == "List<int>":
                    self.value = self._get_list('0')
                else:
                    raise Exception(f'Invalid id field type: {field.name} {field.py_field_type}')
            # Assume that this is a name and a string.
            elif FieldDoc.RE_NAME.match(field.name) is not None:
                self.value = '"name"'
            elif field.cs_field_type == 'byte[]':
                self.value = self._get_array('0')
            # Use an example value derived from the field name.
            elif field.name in FieldDoc.EXAMPLE_VALUES_BY_PARAMETER_NAME:
                self.value = FieldDoc.EXAMPLE_VALUES_BY_PARAMETER_NAME[field.name]
                if field.cs_field_type == "float":
                    self.value += self._get_float_suffix()
            # Use the default primitive value.
            elif field.cs_field_type == "int" or field.cs_field_type == 'uint':
                self.value = '1'
            elif field.cs_field_type == "string":
                self.value = '"string"'
            elif field.cs_field_type == "float":
                self.value = f'0.75{self._get_float_suffix()}'
            elif field.cs_field_type == "bool":
                self.value = self._get_bool()
            # Use default Unity struct values.
            elif field.cs_field_type == "Vector2":
                self.value = self._get_vector2()
            elif field.cs_field_type == "Vector2Int":
                self.value = self._get_vector2int()
            elif field.cs_field_type == "Vector3":
                self.value = self._get_vector3()
            elif field.cs_field_type == "Vector3Int":
                self.value = self._get_vector3int()
            elif field.cs_field_type == "Vector4":
                self.value = self._get_vector4()
            elif field.cs_field_type == "Color":
                self.value = self._get_color()
            elif field.cs_field_type == "Quaternion":
                self.value = self._get_quaternion()
            elif field.cs_field_type == "Vector3[]":
                self.value = self._get_array(self._get_vector3())
            elif field.cs_field_type == "Vector2Int[]":
                self.value = self._get_list(self._get_vector2int())
            # Use the default empty list of integers.
            elif field.cs_field_type == "int[]":
                self.value = self._get_array('0')
            elif field.cs_field_type == "List<int>":
                self.value = self._get_list('0')
            # Use default enum values that aren't in the assembly.
            elif field.cs_field_type == "ImpactMaterialUnsized":
                self.value, self.enum_table = self._get_impact_material()
            # Use a default enum value.
            elif field.cs_field_type in enums:
                enum = enums[field.cs_field_type]
                self.value = self._get_enum_value(enum.members[0], enum)
                self.enum_table = self._get_enum_table(enum)
            elif field.cs_field_type == "ClothMaterial":
                self.value = self._get_cloth_material()
            elif field.cs_field_type == "FluidBase":
                self.value = self._get_fluid_base()
            elif field.cs_field_type == "EmitterShapeBase":
                self.value = self._get_emitter()
            else:
                self.value = self._get_missing_type(field)

    @abstractmethod
    def _get_name(self, field: Field) -> str:
        """
        :param field: The field.

        :return: A code example for a field that defines a name.
        """

        raise Exception()

    @abstractmethod
    def _get_type(self, field: Field, enums: Dict[str, EnumType]) -> str:
        """
        :param field: The field.
        :param enums: All EnumTypes in the assembly.

        :return: A string describing the enum's type.
        """

        raise Exception()

    @abstractmethod
    def _get_default_value(self, field: Field) -> Optional[str]:
        """
        :param field: The field.

        :return: The field's default value, if any.
        """

        raise Exception()

    @abstractmethod
    def _get_bool(self) -> str:
        """
        :return: An example boolean value.
        """

        raise Exception()

    @abstractmethod
    def _get_array(self, value: str) -> str:
        """
        :return: An example array value.
        """

        raise Exception()

    @abstractmethod
    def _get_list(self, value: str) -> str:
        """
        :return: An example list value.
        """

        raise Exception()

    @abstractmethod
    def _get_float_suffix(self) -> str:
        """
        :return: The suffix used for float values.
        """

        raise Exception()

    @abstractmethod
    def _get_vector2(self) -> str:
        """
        :return: An example Vector2 value.
        """

        raise Exception()

    @abstractmethod
    def _get_vector2int(self) -> str:
        """
        :return: An example Vector2Int value.
        """

        raise Exception()

    @abstractmethod
    def _get_vector3(self) -> str:
        """
        :return: An example Vector3 value.
        """

        raise Exception()

    @abstractmethod
    def _get_vector3int(self) -> str:
        """
        :return: An example Vector3 value.
        """

        raise Exception()

    @abstractmethod
    def _get_vector4(self) -> str:
        """
        :return: An example Vector4 value.
        """

        raise Exception()

    @abstractmethod
    def _get_color(self) -> str:
        """
        :return: An example Color value.
        """

        raise Exception()

    @abstractmethod
    def _get_quaternion(self) -> str:
        """
        :return: An example Quaternion value.
        """

        raise Exception()

    @abstractmethod
    def _get_impact_material(self) -> Tuple[str, str]:
        """
        :return: An example ImpactMaterial value.
        """

        raise Exception()

    @abstractmethod
    def _get_cloth_material(self) -> str:
        """
        :return: An example ClothMaterial value.
        """

        raise Exception()

    @abstractmethod
    def _get_fluid_base(self) -> str:
        """
        :return: An example FluidBase value.
        """

        raise Exception()

    @abstractmethod
    def _get_emitter(self) -> str:
        """
        :return: An example Emitter value.
        """

        raise Exception()

    @abstractmethod
    def _get_enum_value(self, member: EnumMember, enum: EnumType) -> str:
        """
        :param member: The example EnumMember.
        :param enum: The enum that this member belongs to.

        :return: An example value.
        """

        raise Exception()

    def _get_missing_type(self, field: Field) -> str:
        """
        :param field: The field.

        :return: An example value if the type is missing.
        """

        raise Exception(field.name, field.cs_field_type, field.cs_default_value)

    @staticmethod
    def _get_enum_table(enum: EnumType) -> str:
        """
        :param enum: An EnumType.

        :return: A table of enum members.
        """

        enum_table = f"#### {enum.name}\n\n"
        return enum_table + enum.get_table()
