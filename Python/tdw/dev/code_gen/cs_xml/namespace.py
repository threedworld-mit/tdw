from typing import List
from xml.etree import ElementTree as Et
from tdw.dev.code_gen.cs_xml.enum_type import EnumType, enum_from_xml
from tdw.dev.code_gen.cs_xml.struct import Struct
from tdw.dev.code_gen.cs_xml.klass import Klass
from tdw.dev.code_gen.cs_xml.util import get_root


class Namespace:
    """
    Definition of a C# namespace.
    """

    def __init__(self, filename: str, structs: List[Struct], klasses: List[Klass]):
        """
        :param filename: The name of the namespace XML file.
        :param structs: Every struct in the assembly.
        :param klasses: Every class in the assembly.
        """

        root: Et.ElementTree = get_root(filename)
        compound_def = root.find("compounddef")
        """:field
        The name of the namespace.
        """
        self.name: str = compound_def.find("compoundname").text
        """:field
        The namespace's EnumTypes.
        """
        self.enums: List[EnumType] = list()
        for section in compound_def.findall("sectiondef"):
            if section.attrib["kind"] == "enum":
                for member in section.findall("memberdef"):
                    self.enums.append(enum_from_xml(member, self.name))
        """:field
        The namespace's structs.
        """
        self.structs: List[Struct] = [s for s in structs if s.namespace == self.name]
        """:field
        The namespace's classes.
        """
        self.klasses: List[Klass] = [s for s in klasses if s.namespace == self.name]
