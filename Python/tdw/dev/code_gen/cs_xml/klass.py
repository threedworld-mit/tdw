import re
from pathlib import Path
from typing import List, Optional, Dict
from xml.etree import ElementTree as Et
from inflection import underscore
from tdw.dev.code_gen.cs_xml.struct import Struct
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.py_field import PyField
from tdw.dev.code_gen.cs_xml.enum_type import EnumType, enum_from_xml
from tdw.dev.code_gen.cs_xml.field_doc_gen.json_field_doc import JsonFieldDoc


class Klass(Struct):
    """
    Definition of a class. This is a subclass of `Struct` that includes class inheritance.
    """

    def __init__(self, element: Et.Element):
        """
        :param element: The root XML element.
        """

        super().__init__(element=element)
        # Double-check the file itself.
        if not self.abstract:
            text = Path(self.location).read_text(encoding="utf-8")
            if f"public abstract class {self.name}" in text:
                self.abstract = True
        """:field
        If True, this script is in TDWThirdParty.
        """
        self.tdw_third_party: bool = "TDWThirdParty" in self.location
        """:field
        The IDs of all child classes. This is used to determine class inheritance.
        """
        self.child_ids: List[str] = list()
        for derived_compound_ref in element.findall("derivedcompoundref"):
            self.child_ids.append(derived_compound_ref.attrib["refid"])
        base_compound_ref = element.find("basecompoundref")
        """:field
        The parent class's ID. Can be None.
        """
        self.parent_id: Optional[str] = None
        if base_compound_ref is not None:
            self.parent = base_compound_ref.text.split(".")[-1]
            self.parent = re.sub(r"< (.*?) >", "", self.parent).replace(">", "")
            if "::" in self.parent:
                self.parent = self.parent.split("::")[-1]
            if "refid" in base_compound_ref.attrib:
                self.parent_id = base_compound_ref.attrib["refid"]
        # Remove TrialStatus.
        self.fields = [f for f in self.fields if f.cs_field_type != "TrialStatus"]
        # Get my enums.
        self.enums: List[EnumType] = list()
        for section in element.findall("sectiondef"):
            if section.attrib["kind"] == "public-type":
                for member in section.findall("memberdef"):
                    if member.attrib["kind"] == "enum":
                        self.enums.append(enum_from_xml(member, namespace=self.namespace))
        # This will be set in Assembly.
        self.is_command: bool = self.name == "Command"
        if self.import_path == "tdw_input":
            self.import_path = "tdw.commands"

    def get_imports(self) -> List[str]:
        imports = super().get_imports()
        # Insert ABC.
        if self.abstract:
            imports.insert(0, "from abc import ABC")
        if self.parent is not None:
            # Handle Trial manually for test trials.
            if self.parent == "Trial":
                imports.append("from tdw.webgl.trials.trial import Trial")
            # Auto-generate the import statement.
            else:
                imports.append(
                    f"from {self.import_path}.{underscore(self.parent)} import {self.parent}")
        return list(sorted(set(imports)))

    def get_json_doc(self, enums: Dict[str, EnumType]) -> str:
        """
        :param enums: All EnumTypes in the assembly.

        :return: JSON documentation and code examples.
        """

        cs_fields = self._get_fields_for_doc()
        py_fields = [PyField(f) for f in cs_fields]
        command = '{"$type": "' + underscore(self.name) + '"'
        non_default_fields = [f for f in py_fields if f.py_default_value is None]
        if len(non_default_fields) > 0:
            command += ', '
            command += ', '.join(['"' + f.field.name + '": ' + JsonFieldDoc(f.field, enums).value for f in non_default_fields])
        doc = f'```python\n{command}' + '}\n```'
        default_fields = [f for f in py_fields if f.py_default_value is not None]
        # There are no default values. Only include the minimal example.
        if len(default_fields) > 0:
            if command.endswith('"') or len(non_default_fields) > 0:
                command += ', '
            command += ', '.join(['"' + f.field.name + '": ' + f.py_default_value for f in default_fields])
            command += '}'
            doc += f'\n\n```python\n{command}\n```'
        return doc

    def _get_fields_for_doc(self) -> List[Field]:
        fields = super()._get_fields_for_doc()[:]
        fields.extend(self.inherited_fields)
        return fields

    def _get_import_path(self) -> str:
        if self.is_command:
            return f"from tdw.commands import {self.name}"
        else:
            return super()._get_import_path()
