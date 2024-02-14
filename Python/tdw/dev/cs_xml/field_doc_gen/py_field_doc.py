from typing import Dict
from tdw.dev.cs_xml.field import Field
from tdw.dev.cs_xml.enum_type import EnumType, enum_from_py
from tdw.dev.cs_xml.util import PY_ENUM_TYPES, PY_IMPORT_TYPES
from tdw.dev.cs_xml.field_doc_gen.py_json_field_doc import PyJsonFieldDoc


class PyFieldDoc(PyJsonFieldDoc):
    """
    Generate an example value for a Python field.
    """
    
    def _get_name(self, field: Field) -> str:
        return field.name

    def _get_bool(self) -> str:
        return 'True'

    def _get_cloth_material(self) -> str:
        return 'CLOTH_MATERIALS["silk"]'

    def _get_fluid_base(self) -> str:
        return 'FLUIDS["water"]'

    def _get_emitter(self) -> str:
        return 'DiskEmitter()'

    def _get_type(self, field: Field, enums: Dict[str, EnumType]) -> str:
        return field.py_field_type

    def _get_enum_value_suffix(self) -> str:
        return ''

    def _get_missing_type(self, field: Field) -> str:
        if field.py_field_type in PY_ENUM_TYPES:
            enum = enum_from_py(name=field.py_field_type, import_path=PY_IMPORT_TYPES[field.py_field_type])
            return f'{enum.name}.{enum.members[0].name}'
        elif field.py_field_type.startswith("List["):
            return '[]'
        elif field.cs_field_type == 'Axis':
            return '"yaw"'
        else:
            return super()._get_missing_type(field)
