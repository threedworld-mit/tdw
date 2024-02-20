import re
from typing import List
from importlib import import_module
from xml.etree import ElementTree as Et
from inflection import underscore
from tdw.dev.code_gen.cs_xml.enum_member import EnumMember, enum_member_from_xml
from tdw.dev.code_gen.cs_xml.util import parse_para
from tdw.dev.config import Config


class EnumType:
    """
    Definition of a C# enum type.
    """

    def __init__(self, namespace: str, name: str, description: str, members: List[EnumMember]):
        """
        :param namespace: The namespace that the enum belongs to.
        :param name: The name of the enum.
        :param description: A description of the enum.
        :param members: A list of enum members.
        """

        """:field
        The namespace that the enum belongs to.
        """
        self.namespace: str = namespace
        """:field
        The name of the enum.
        """
        self.name: str = name
        """:field
        A description of the enum.
        """
        self.description: str = description
        """:field
        A list of enum members.
        """
        self.members: List[EnumMember] = members
        """:field
        This enum type's import path, if it were a Python class.
        """
        self.import_path: str = ".".join([underscore(n) for n in namespace.split("::")]).replace("web_gl", "webgl")
        if self.import_path == "tdw_input":
            self.import_path = "tdw.commands.enums"

    def get_py_doc(self) -> str:
        """
        :return: Documentation to a code-genned Python enum class.
        """

        doc = (f"# {self.name}\n\n"
               f"{self.description}\n\n"
               f"```python\n"
               f"from tdw.{self.import_path}.{underscore(self.name)} import {self.name}\n\n"
               f"v = {self.name}.{self.members[0].name}\n```\n\n")
        doc += self.get_table()
        return doc

    def get_cs_doc(self) -> str:
        """
        :return: Documentation for the original C# enum class.
        """

        doc = (f"# {self.name}\n\n"
               f"{self.description}\n\n```csharp\n"
               f"using {self.namespace.replace('::', '.')};\n\n"
               f"// More code here.\n\n"
               f"v = {self.name}.{self.members[0].name};\n```\n\n")
        doc += self.get_table()
        return doc

    def get_table(self, string_values: bool = False) -> str:
        """
        :param string_values: If true, encapsulate the enum member names in quotes. This is used for some Python documentation.

        :return: A markdown table of enum members.
        """

        table = "| Value | Description |\n| --- | --- |\n"
        rows = []
        for member in self.members:
            if string_values:
                rows.append(f'| `"{member.name}"` | {member.description} |')
            else:
                rows.append(f'| {member.name} | {member.description} |')
        table += "\n".join(rows)
        return table


def enum_from_xml(element: Et.Element, namespace: str) -> EnumType:
    """
    :param element: An XML element.
    :param namespace: The enum's namespace.

    :return: An EnumType.
    """

    return EnumType(namespace=namespace,
                    name=element.find("name").text,
                    description=parse_para(element.find("briefdescription")),
                    members=[enum_member_from_xml(e) for e in element.findall("enumvalue")])


def enums_from_struct_xml(element: Et.Element) -> List[EnumType]:
    """
    :param element: An XML elemement for a struct or class.

    :return: A list of the struct's or class's child EnumTypes.
    """

    enums: List[EnumType] = list()
    compound_name: str = element.find("compoundname").text
    compound_name_split: List[str] = compound_name.split("::")
    name: str = compound_name_split[-1]
    name = re.sub(r"< (.*?) >", "", name)
    namespace: str = "::".join(compound_name_split[:-1])
    for section in element.findall("sectiondef"):
        if section.attrib["kind"] == "public-type":
            for member in section.findall("memberdef"):
                if member.attrib["kind"] == "enum":
                    enum = enum_from_xml(member, namespace=namespace)
                    enum.name = f'{name}.{enum.name}'
                    enums.append(enum)
    return enums


def enum_from_py(name: str, import_path: str, add_member_descriptions: bool = False) -> EnumType:
    """
    :param name: The name of the enum Python class.
    :param import_path: The Python import path.
    :param add_member_descriptions: If True, try to add descriptions for each enum member.

    :return: An EnumType.
    """

    # Import the enum and get its members.
    members = []
    namespace = import_path.replace('.', '::')
    m = import_module(f'{import_path}.{underscore(name)}')
    attributes = getattr(m, name)
    if add_member_descriptions:
        # Read the file.
        text = Config().tdw_path.joinpath("Python").joinpath(import_path.replace(".", "/")).joinpath(underscore(name) + ".py").resolve().read_text()
        # Parse the member descriptions.
        member_descriptions = re.findall(r" {2}# (.*)", text, flags=re.MULTILINE)
        # Set each member and its description.
        for a, d in zip(attributes, member_descriptions):
            members.append(EnumMember(name=a, description=d))
    else:
        for a in attributes:
            members.append(EnumMember(name=a, description=''))
    return EnumType(name=name, description='', namespace=namespace, members=members)
