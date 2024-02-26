import re
from typing import Optional, Dict
from xml.etree import ElementTree as Et
from tdw.dev.code_gen.cs_xml.util import parse_para, parse_ref, html_to_markdown


class Field:
    """
    A field in a struct or class.
    """

    """:class_var
    Regex used to find numerical default values.
    """
    RE_NUMBERS: re.Pattern = re.compile(r'(-?\d+\.?\d*|\d+)')
    """:class_var
    Regex to find actual double-quotes in the XML data.
    """
    RE_QUOTES: re.Pattern = re.compile(r'"(.*?)"')
    """:class_var
    Regex to find boolean default values.
    """
    RE_BOOL: re.Pattern = re.compile(r'(true|false)')
    """:class_var
    Regex to find dictionary default values.
    """
    RE_NEW_DICTIONARY: re.Pattern = re.compile(r'new Dictionary<\w+, \w+>\(\)')
    """:class_var
    Regex to find array default values.
    """
    RE_NEW_ARRAY: re.Pattern = re.compile(r'new \w+\[0]')
    """:class_var
    When generating Python documentation, use these strings as the default value for these C# enum types.
    """
    CS_ENUM_DEFAULTS: Dict[str, str] = {'Frequency': '"once"',
                                        'AntiAliasingMode': '"subpixel"',
                                        'DetectionMode': '"continuous_dynamic"',
                                        'AssetBundleType': '"models"'}
    """:class_var
    Default C# values. Key = The field name.
    """
    CS_DEFAULT_VALUES: Dict[str, str] = {"max_retries": "Req.DEFAULT_MAX_RETRIES",
                                         "timeout": "Req.DEFAULT_TIMEOUT"}

    def __init__(self, element: Et.Element):
        """
        :param element: An XML element.
        """

        """:field
        The field's doxygen ID. This is used to figure out class inheritance.
        """
        self.id: str = element.attrib["id"]
        """:field
        The name of the field.
        """
        self.name: str = element.find("name").text
        """:field
        A description of the field.
        """
        self.description: str = html_to_markdown(parse_para(element.find("briefdescription")))
        """:field
        If True, this is is a static field.
        """
        self.static: bool = "static" in element.attrib and element.attrib["static"] == "yes"
        """:field
        If True, this is a public field.
        """
        self.public: bool = "prot" in element.attrib and element.attrib["prot"] == "public"
        # Convert the field type from C# to Python.
        field_type = element.find("type").text
        if field_type is None or field_type == "readonly ":
            field_type = element.find("type").find("ref").text
            raw = str(Et.tostring(element, "utf-8"))
            if "[]" in raw:
                field_type += "[]"
        # Collection with a ref tag.
        if field_type.endswith("< "):
            field_type = parse_ref(element.find("type")).replace(" &gt;", ">").replace("< ", "<")
        field_type = field_type.replace("< ", "<").replace(" >", ">")
        """:field
        If True, this is a constant, not a field.
        """
        self.constant: bool = False
        # This is a constant.
        if field_type.startswith("const "):
            self.constant = True
            field_type = field_type.replace("const ", "")
        """:field
        If True, this field is read-only.
        """
        self.readonly: bool = False
        # This is readonly.
        if "readonly " in field_type:
            self.readonly = True
            field_type = field_type.replace("readonly ", "")
        """:field
        The field's C# type.
        """
        self.cs_field_type: str = field_type
        """:field
        If True, the field type is a collection (list, dictionary, etc.).
        """
        self.is_collection: bool = self.cs_field_type.startswith("List<") or self.cs_field_type.startswith("Dictionary<") or self.cs_field_type.endswith("[]")
        """:field
        The initializer XML element.
        """
        self.initializer: Et.Element = element.find("initializer")
        if self.initializer is None:
            """:field
            The default value in the original C# code. Can be None.
            """
            self.cs_default_value: Optional[str] = None
        else:
            self.cs_default_value: str = self.initializer.text.split("=")[1].strip()
            # Dictionary.
            if self.cs_default_value == "new Dictionary<":
                self.cs_default_value = parse_ref(self.initializer).replace("&gt;", ">").replace("< ", "<").split("=")[1].strip()
            # Array.
            elif self.cs_default_value == "new":
                self.cs_default_value = parse_ref(self.initializer).split("=")[1].strip()
            # Fix quotes.
            self.cs_default_value = self.cs_default_value.replace('&quot;', '"')
            if self.name in Field.CS_DEFAULT_VALUES and self.cs_default_value == "":
                self.cs_default_value = Field.CS_DEFAULT_VALUES[self.name]
