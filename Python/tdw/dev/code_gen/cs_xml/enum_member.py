from xml.etree import ElementTree as Et
from tdw.dev.code_gen.cs_xml.util import parse_para


class EnumMember:
    """
    A member of a C# enum.
    """

    def __init__(self, name: str, description: str):
        """
        :param name: The name of the enum member.
        :param description: A description of the enum member.
        """

        """:field
        The name of the enum member.
        """
        self.name: str = name
        """:field
        A description of the enum member.
        """
        self.description: str = description


def enum_member_from_xml(element: Et.Element) -> EnumMember:
    """
    :param element: An XML element.

    :return: An EnumMember.
    """

    return EnumMember(name=element.find("name").text, description=parse_para(element.find("briefdescription")))
