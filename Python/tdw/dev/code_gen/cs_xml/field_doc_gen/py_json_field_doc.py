from abc import ABC, abstractmethod
from typing import final, Optional, Tuple
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.field_doc_gen.field_doc import FieldDoc
from tdw.dev.code_gen.cs_xml.enum_member import EnumMember
from tdw.dev.code_gen.cs_xml.enum_type import EnumType
from tdw.dev.code_gen.cs_xml.util import STRS


class PyJsonFieldDoc(FieldDoc, ABC):
    """
    Abstract base class for Python or JSON example field value generators.
    """

    @final
    def _get_default_value(self, field: Field) -> Optional[str]:
        return field.py_default_value

    @final
    def _get_float_suffix(self) -> str:
        return ""

    @final
    def _get_array(self, value: str) -> str:
        return f'[{value}]'

    @final
    def _get_list(self, value: str) -> str:
        return self._get_array(value)

    @final
    def _get_color(self) -> str:
        return '{"r": 1, "g": 0.5, "b": 0, "a": 1}'

    @final
    def _get_quaternion(self) -> str:
        return '{"x": 0, "y": 0, "z": 0, "w": 1}'

    @final
    def _get_vector4(self) -> str:
        return self._get_quaternion()

    @final
    def _get_vector2(self) -> str:
        return '{"x": 0, "y": 0}'

    @final
    def _get_vector2int(self) -> str:
        return self._get_vector2()

    @final
    def _get_vector3(self) -> str:
        return '{"x": 0, "y": 0, "z": 0}'

    @final
    def _get_vector3int(self) -> str:
        return self._get_vector3()

    @final
    def _get_impact_material(self) -> Tuple[str, str]:
        value = f'ImpactMaterial.wood_medium{self._get_enum_value_suffix()}'
        enum_table = f"#### ImpactMaterial\n\nThese are the materials currently supported for impact sounds in Clatter.\n\n| Value | Description |\n| --- | --- |"
        rows = []
        for member in ImpactMaterial:
            rows.append(f'| {member.name}{self._get_enum_value_suffix()} | |')
        enum_table += "\n".join(rows)
        return value, enum_table

    @final
    def _get_enum_value(self, member: EnumMember, enum: EnumType) -> str:
        # This enum is represented as a string in the Python API.
        if enum.name in STRS:
            return f'"{member.name}"'
        # This enum is expressed as a Python type.
        else:
            return f'{enum.name}.{enum.members[0].name}{self._get_enum_value_suffix()}'

    @abstractmethod
    def _get_enum_value_suffix(self) -> str:
        raise Exception()
