from typing import Dict
from importlib import import_module
from inflection import underscore
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.enum_type import EnumType
from tdw.dev.code_gen.cs_xml.util import STRS, PY_IMPORT_TYPES, PY_ENUM_TYPES
from tdw.dev.code_gen.cs_xml.field_doc_gen.py_json_field_doc import PyJsonFieldDoc


class JsonFieldDoc(PyJsonFieldDoc):
    """
    Generate an example value for a JSON dictionary key.
    """

    def _get_name(self, field: Field) -> str:
        return f'"{field.name}"'

    def _get_bool(self) -> str:
        return 'True'

    def _get_enum_value_suffix(self) -> str:
        return '.name'

    def _get_type(self, field: Field, enums: Dict[str, EnumType]) -> str:
        if field.cs_field_type in STRS:
            return 'str'
        else:
            return field.py_field_type

    def _get_cloth_material(self) -> str:
        return 'json.dumps(CLOTH_MATERIALS["silk"].__dict__)'

    def _get_fluid_base(self) -> str:
        return 'json.dumps(FLUIDS["water"].__dict__)'

    def _get_emitter(self) -> str:
        return 'json.dumps(DiskEmitter())'

    def _get_missing_type(self, field: Field) -> str:
        if field.py_field_type in PY_ENUM_TYPES:
            m = import_module(f'{PY_IMPORT_TYPES[field.py_field_type]}.{underscore(field.py_field_type)}')
            return f'{list(getattr(m, field.py_field_type))[0]}.name'
        elif field.cs_field_type == "Axis":
            return '"yaw"'
        else:
            return super()._get_missing_type(field)
