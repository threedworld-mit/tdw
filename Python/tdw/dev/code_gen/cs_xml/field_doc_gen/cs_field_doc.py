from typing import Optional, Tuple, Dict
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.field_doc_gen.field_doc import FieldDoc
from tdw.dev.code_gen.cs_xml.enum_member import EnumMember
from tdw.dev.code_gen.cs_xml.enum_type import EnumType


class CsFieldDoc(FieldDoc):
    """
    Generate an example value for a C# field.
    """

    def _get_name(self, field: Field) -> str:
        return field.name

    def _get_bool(self) -> str:
        return 'true'

    def _get_vector4(self) -> str:
        return 'new Vector4(0, 0, 0, 1)'

    def _get_vector3(self) -> str:
        return 'new Vector3(0, 0, 0)'

    def _get_vector3int(self) -> str:
        return 'new Vector3Int(0, 0, 0)'

    def _get_vector2(self) -> str:
        return 'new Vector2(0, 0)'

    def _get_vector2int(self) -> str:
        return 'new Vector2Int(0, 0)'

    def _get_quaternion(self) -> str:
        return 'new Quaternion(0, 0, 0, 1)'

    def _get_color(self) -> str:
        return 'new Color(1, 0, 0)'

    def _get_list(self, value: str) -> str:
        return 'new { ' + value + " }"

    def _get_array(self, value: str) -> str:
        return 'new { ' + value + " }"

    def _get_type(self, field: Field, enums: Dict[str, EnumType]) -> str:
        return field.cs_field_type

    def _get_default_value(self, field: Field) -> Optional[str]:
        return field.cs_default_value

    def _get_emitter(self) -> str:
        return 'new DiskEmitter()'

    def _get_fluid_base(self) -> str:
        return 'new Fluid()'

    def _get_cloth_material(self) -> str:
        return 'new ClothMaterial()'

    def _get_impact_material(self) -> Tuple[str, str]:
        value = f'Clatter.Core.ImpactMaterialUnsized.wood_medium'
        enum_table = f"#### ImpactMaterialUnsized\n\nThese are the materials currently supported for impact sounds in Clatter.\n\n| Value | Description |\n| --- | --- |"
        rows = []
        for member in ImpactMaterial:
            rows.append(f'| {member.name} | |')
        enum_table += "\n".join(rows)
        return value, enum_table

    def _get_enum_value(self, member: EnumMember, enum: EnumType) -> str:
        return f'{enum.name}.{member.name}'

    def _get_float_suffix(self) -> str:
        return 'f'
    
    def _get_missing_type(self, field: Field) -> str:
        if field.cs_field_type == 'RaycastHit':
            return 'new RaycastHit()'
        elif '[]' in field.cs_field_type:
            return f'new {field.cs_field_type.split("[")[0]}[0]'
        elif field.cs_field_type == 'Color32':
            return 'new Color32(255, 0, 0)'
        else:
            return super()._get_missing_type(field)
