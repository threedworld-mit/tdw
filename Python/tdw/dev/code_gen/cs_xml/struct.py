import re
from importlib import import_module
from typing import List, Optional, Dict
from xml.etree import ElementTree as Et
from inflection import underscore, camelize
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.enum_type import EnumType, enum_from_py
from tdw.dev.code_gen.cs_xml.method import Method
from tdw.dev.code_gen.cs_xml.util import parse_para, CS_TO_PY_TYPES, BUILTIN_TYPES, PY_IMPORT_TYPES, STRS, PY_ENUM_TYPES
from tdw.dev.code_gen.cs_xml.field_doc_gen.py_field_doc import PyFieldDoc
from tdw.dev.code_gen.cs_xml.field_doc_gen.cs_field_doc import CsFieldDoc


class Struct:
    """
    Definition of a C# struct. This is also the base class of a C# class definition.
    """

    def __init__(self, element: Et.Element):
        """
        :param element: The root XML element.
        """

        """:field
        If True, the struct is public.
        """
        self.public: bool = element.attrib["prot"] == "public"
        """:field
        If True, the struct is static.
        """
        self.static: bool = "static" in element.attrib and element.attrib["static"] == "yes"
        """:field
        If True, the class is abstract. For structs, this is always False.
        """
        self.abstract: bool = "abstract" in element.attrib and element.attrib["abstract"] == "yes"
        """:field
        The doxygen ID of this struct. This is used for class inheritance.
        """
        self.id: str = element.attrib["id"]
        compound_name: str = element.find("compoundname").text
        compound_name_split: List[str] = compound_name.split("::")
        """:field
        The struct name.
        """
        self.name: str = compound_name_split[-1]
        self.name = re.sub(r"< (.*?) >", "", self.name)
        self.namespace: str = "::".join(compound_name_split[:-1])
        """:field
        The Python import path, if this were to be code-genned.
        """
        self.import_path: str = ".".join([underscore(n) for n in compound_name_split[:-1]]).replace("web_gl", "webgl")
        if "tdw_input" in self.import_path:
            self.import_path = "tdw.commands"
        """:field
        A description of the struct.
        """
        self.description: str = parse_para(element.find("briefdescription"))
        """:field
        The ID of this class's parent, if any. If this is a struct and not a class, this field's value is always None.
        """
        self.parent: Optional[str] = None
        """:field
        The struct's fields.
        """
        self.fields: List[Field] = list()
        """:field
        The struct's methods.
        """
        self.methods: List[Method] = list()
        for section in element.findall("sectiondef"):
            section_kind = section.attrib["kind"]
            if section_kind == "public-attrib":
                for member in section.findall("memberdef"):
                    if member.attrib["kind"] == "variable":
                        self.fields.append(Field(element=member))
            elif section_kind == "public-static-func" or section_kind == "public-func":
                for member in section.findall("memberdef"):
                    if member.attrib["kind"] == "function":
                        self.methods.append(Method(element=member))
        """:field
        The classe's inherited fields. For structs, this is always empty.
        """
        self.inherited_fields: List[Field] = list()
        """:field
        The path to the C# file.
        """
        self.location: str = element.find("location").attrib["file"]
        """:field
        If True, this is a type of Command.
        """
        self.is_command: bool = False

    def get_imports(self) -> List[str]:
        """
        :return: A list of all Python import statements that this class requires.
        """

        # Get import paths.
        typing_imports: List[str] = list()
        imports: List[str] = list()
        fields = self.fields[:]
        fields.extend([f for f in self.inherited_fields if f.py_field_type != "TrialStatus"])
        for field in fields:
            if "List[" in field.py_field_type:
                typing_imports.append("List")
            if "Dict[" in field.py_field_type:
                typing_imports.append("Dict")
            is_collection = False
            if field.py_field_type.startswith("List["):
                is_collection = True
            elif field.py_field_type.startswith("Dict["):
                is_collection = True
            elif field.py_field_type in CS_TO_PY_TYPES or field.py_field_type in BUILTIN_TYPES:
                continue
            elif field.py_field_type == "ClothVolumeType":
                imports.append("from tdw.obi_data.cloth.volume_type import ClothVolumeType")
            elif field.py_field_type in PY_IMPORT_TYPES:
                imports.append(
                    f"from {PY_IMPORT_TYPES[field.py_field_type]}.{underscore(field.py_field_type)} import {field.py_field_type}")
            else:
                raise Exception("Invalid field type: " + field.name + " " + field.py_field_type)
            if is_collection:
                collection_types = re.search(r"(?!.*\[)(.*?)]", field.py_field_type).group(1).split(",")
                collection_types = [collection_type.strip() for collection_type in collection_types]
                for collection_type in collection_types:
                    if collection_type in CS_TO_PY_TYPES or collection_type in BUILTIN_TYPES:
                        continue
                    elif collection_type in PY_IMPORT_TYPES:
                        imports.append(
                            f"from {PY_IMPORT_TYPES[collection_type]}.{underscore(collection_type)} import {collection_type}")
                    else:
                        raise Exception("Invalid field type: " + field.name + " " + field.py_field_type)
        if len(typing_imports) > 0:
            imports.insert(0, "from typing import " + ", ".join(sorted(list(set(typing_imports)))))
        return list(sorted(set(imports)))

    def get_py_doc(self, enums: Dict[str, EnumType]) -> str:
        """
        :param enums: All EnumTypes in the assembly.

        :return: Documentation for a code-genned Python class.
        """

        fields = self._get_fields_for_doc()
        imports = [self._get_import_path()]
        for f in fields:
            if f.py_field_type in PY_IMPORT_TYPES:
                import_path = f"{PY_IMPORT_TYPES[f.py_field_type]}.{underscore(f.py_field_type)}"
                imports.append(f"from {import_path} import {f.py_field_type}")
        code_prefix = "```python\n" + "\n".join(list(sorted(set(imports)))) + f"\n\n{underscore(self.name)} = {self.name}("
        doc = f"# {self.name}\n\n{self.description.split('doc_gen_tags')[0].strip()}\n\n{code_prefix}"
        # Get the fields.
        field_rows = []
        constructor_fields = []
        # Close the code example without adding fields.
        if len(fields) == 0:
            doc += ")\n```\n\n"
        else:
            # Add fields that don't have a default value.
            non_default_fields = [f for f in fields if f.py_default_value is None]
            for f in non_default_fields:
                # Add an import statement.
                if f.py_field_type in PY_IMPORT_TYPES:
                    import_path = f"{PY_IMPORT_TYPES[f.py_field_type]}.{underscore(f.py_field_type)}"
                    imports.append(f"from {import_path} import {f.py_field_type}")
                    if f.py_field_type in PY_ENUM_TYPES:
                        m = import_module(import_path)
                        value = f"{f.py_field_type}.{list(getattr(m, f.py_field_type))[0].name}"
                    else:
                        value = f.name
                elif f.cs_field_type in DEFAULT_VALUES:
                    value = DEFAULT_VALUES[f.cs_field_type]
                # String enum.
                elif f.cs_field_type in enums:
                    value = f'"{enums[f.cs_field_type].members[0].name}"'
                else:
                    value = PyFieldDoc(f, enums).value
                constructor_fields.append(value)
                field_rows.append(f"| `{f.name}` | {f.py_field_type} | {f.description} | |")
            # Append the fields that don't have a default value to the constructor.
            doc += ", ".join(constructor_fields) + ")\n```\n\n"
            # Add fields that have a default value.
            default_fields = [f for f in fields if f.py_default_value is not None]
            if len(default_fields) > 0:
                for f in default_fields:
                    constructor_fields.append(f'{f.name}={f.py_default_value}')
                    field_rows.append(f"| `{f.name}` | {f.py_field_type} | {f.description} | {f.py_default_value} |")
                # Add the constructor fields.
                doc += code_prefix + ", ".join(constructor_fields) + ")\n```\n\n"
            # Add the table.
            doc += "| Parameter | Type | Description | Default |\n| --- | --- | --- | --- |\n"
            doc += "\n".join(field_rows)
            # Add enum tables.
            cs_enum_names = []
            py_enum_names = []
            for field in fields:
                if field.cs_field_type in enums:
                    cs_enum_names.append(field.cs_field_type)
                elif field.py_field_type in PY_ENUM_TYPES:
                    py_enum_names.append(field.py_field_type)
            enum_tables = []
            for enum_name in sorted(set(cs_enum_names)):
                enum = enums[enum_name]
                if enum_name in STRS:
                    enum_tables.append(f"#### {enum_name}\n\n"
                                       f"{enum.description}\n\n{enum.get_table(string_values=True)}")
                else:
                    enum_tables.append(f"#### {enum_name}\n\n```python\n"
                                       f"from {enum.import_path}.{underscore(enum.name)} import {enum.name}\n```\n\n"
                                       f"{enum.description}\n\n{enum.get_table()}")
            for enum_name in sorted(set(py_enum_names)):
                enum = enum_from_py(enum_name, PY_IMPORT_TYPES[enum_name])
                enum_tables.append(f"#### {enum_name}\n\n```python\n"
                                   f"from {enum.import_path}.{underscore(enum.name)} import {enum.name}\n```\n\n"
                                   f"{enum.description}\n\n{enum.get_table()}")
            if len(enum_tables) > 0:
                doc += "\n\n" + "\n\n".join(enum_tables)
        return doc

    def get_cs_doc(self, methods: bool, enums: Dict[str, EnumType], static: bool = False) -> str:
        """
        :param methods: If True, include methods.
        :param enums: All EnumTypes in the assembly.
        :param static: If True, this is a static class.

        :return: Documentation for the original C# struct.
        """

        doc = f"# {self.name}\n\n{self.description}\n\n"
        struct_namespace = self.namespace.replace('::', '.').strip()
        usings = []
        if struct_namespace != "":
            usings.append(f"using {struct_namespace};")
        # Get the fields.
        fields = self._get_fields_for_doc()
        for f in fields:
            if f.cs_field_type in enums:
                enum_namespace = enums[f.cs_field_type].namespace.replace('::', '.').strip()
                if enum_namespace != "":
                    usings.append(f"using {enum_namespace};")
            elif f.cs_field_type[0].isupper():
                if f.cs_field_type.startswith("List<") or f.cs_field_type.startswith("Dictionary<"):
                    usings.append("using System.Collections.Generic;")
                if f.cs_field_type not in NO_NAMESPACES:
                    got_namespace = False
                    for namespace in NAMESPACES:
                        for member_name in NAMESPACES[namespace]:
                            if member_name == f.cs_field_type:
                                usings.append(f"using {namespace};")
                                got_namespace = True
                                break
                    if not got_namespace:
                        raise Exception(f.name, f.cs_field_type, f.description)
        code_prefix = f"```csharp\n" + "\n".join(list(sorted(set(usings))))
        variable_name = camelize(self.name, uppercase_first_letter=False)
        if self.is_command:
            code_suffix = f"commands.Enqueue({variable_name});"
        else:
            code_suffix = ""
        if static:
            code_prefix += "\n```\n\n"
        else:
            code_prefix += f"\n\n// More code here.\n\n{self.name} {variable_name} = new {self.name}();"
        if self.abstract:
            doc += "*Abstract class*\n\n"
        field_rows = []
        field_assignments = []
        # Close the code example without adding fields.
        if len(fields) == 0:
            if not self.abstract and not static:
                doc += f"{code_prefix}\n{code_suffix}\n```\n\n"
        else:
            # Add fields that don't have a default value.
            non_default_fields = [f for f in fields if f.cs_default_value is None]
            for f in non_default_fields:
                # Add an import statement.
                # String enum.
                if f.cs_field_type in enums:
                    e = enums[f.cs_field_type]
                    value = f'{e.name}.{e.members[0].name}'
                else:
                    value = CsFieldDoc(f, enums).value
                field_assignments.append(f"{self.name}.{f.name} = {value};")
                field_rows.append(f"| `{f.name}` | {f.cs_field_type} | {f.description} | |")
            # Add field assignment statements.
            if not self.abstract and not static:
                if len(field_assignments) > 0:
                    doc += f"{code_prefix}\n" + "\n".join(field_assignments) + f"\n{code_suffix}\n```\n\n"
                else:
                    doc += f"{code_prefix}\n{code_suffix}\n```\n\n"
            # Add fields that have a default value.
            default_fields = [f for f in fields if f.cs_default_value is not None]
            if len(default_fields) > 0:
                for f in default_fields:
                    default_value = f.cs_default_value.replace("\n", "")
                    field_assignments.append(f"{self.name}.{f.name} = {default_value};")
                    field_rows.append(f"| `{f.name}` | {f.cs_field_type} | {f.description} | {default_value} |")
                # Add field assignment statements.
                if not self.abstract and not static:
                    doc += f"{code_prefix}\n" + "\n".join(field_assignments) + f"\n{code_suffix}\n```\n\n"
            # Add the table.
            doc += "## Fields\n\n"
            doc += "| Parameter | Type | Description | Default |\n| --- | --- | --- | --- |\n"
            doc += "\n".join(field_rows)
        ms = [m for m in self.methods if m.public]
        if methods and len(ms) > 0:
            if len(fields) > 0:
                doc += "\n\n"
            doc += "## Methods\n\n"
            # Build a table of contents.
            doc += "\n".join([f"- [{m.name}](#{m.name.replace(' ', '-')})" for m in ms]) + "\n\n"
            doc += "\n\n***\n\n".join([m.get_cs_doc() for m in ms])
        # Add enum tables.
        enum_names = []
        for field in fields:
            if field.cs_field_type in enums:
                enum_names.append(field.cs_field_type)
        enum_tables = []
        for enum_name in sorted(set(enum_names)):
            enum = enums[enum_name]
            enum_text = f"#### {enum_name}\n\n"
            if enum.namespace != "":
                enum_text += (f"```csharp\nusing {enum.namespace};\n\n// More code here.\n\n"
                              f"{enum.name} {camelize(enum.name.split('.')[0], uppercase_first_letter=False)} = {enum.name}.{enum.members[0].name};\n```\n\n")
            enum_text += f"{enum.description}\n\n{enum.get_table()}"
            enum_tables.append(enum_text)
        if len(enum_tables) > 0:
            doc += "\n\n" + "\n\n".join(enum_tables)
        return doc

    def _get_fields_for_doc(self) -> List[Field]:
        """
        :return: The fields that will be included in the documentation.
        """

        return self.fields

    def _get_import_path(self) -> str:
        """
        :return: This struct's Python import path.
        """
        return f"from tdw.{self.import_path}.{underscore(self.name)} import {self.name}"


DEFAULT_VALUES = {'AvatarType': '"A_Img_Caps_Kinematic"'}
NAMESPACES = {'UnityEngine': ['Vector3', 'Vector3[]', 'Vector3Int', 'Vector2', 'Vector2Int', 'Quaternion', 'Color',
                              'Vector4[]', 'Vector2Int[]'],
              'ProcGen': ['CardinalDirection[]'],
              'FBOutput': ['List<PassMask>'],
              'Clatter.Core': ['ImpactMaterialUnsized', 'ScrapeMaterial', 'AudioEventType'],
              'TDW.Obi': ['Dictionary<TetherParticleGroup, TetherType>', 'ClothMaterial', 'FluidBase',
                          'EmitterShapeBase'],
              'TDW.Replicant': ['ReplicantBodyPart[]']}
NO_NAMESPACES = ['List<int>', "List<string>", 'CollisionType[]']
