import re
from typing import Optional, Dict, List
from xml.etree import ElementTree as Et
from tdw.dev.code_gen.cs_xml.util import (parse_para, CS_TO_PY_TYPES, CS_TO_PY_DEFAULT_VALUES, PY_TYPES, STRS, parse_ref)


class Field:
    """
    A field in a struct or class.
    """

    """:class_var
    Regex used to find numerical default values.
    """
    RE_NUMBERS: re.Pattern = re.compile(r'(-?\d+\.?\d*|\d+)')
    """:class_var
    Regex to parse doxygen's double-quote escape strings in the XML data.
    """
    RE_QUOT: re.Pattern = re.compile(r'&quot;(.*?)&quot;')
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
    A dictionary of constants declared in TDWUnity as keys and valid Python default values as values.
    """
    CONST_REPLACEMENTS: Dict[str, str] = {"DEFAULT_BOUNDS": "10",
                                          "DEFAULT_FRICTION": "0.05",
                                          "DEFAULT_SENSOR_NAME": '"SensorContainer"',
                                          "LightManager.SHADOW_STRENGTH": "0.582"}
    """:class_var
    When generating Python documentation, use these strings as the default value for these C# enum types.
    """
    CS_ENUM_DEFAULTS: Dict[str, str] = {'Frequency': '"once"',
                                        'AntiAliasingMode': '"subpixel"',
                                        'DetectionMode': '"continuous_dynamic"',
                                        'AssetBundleType': '"models"'}
    """:class_var
    In Python documentation, these types need None default values.
    """
    CS_MUTABLE_TYPES: List[str] = ["Vector3", "Vector3Int", "Vector2", "Vector2Int", "Color", "Quaternion"]

    def __init__(self, element: Et.Element, py: bool):
        """
        :param element: An XML element.
        :param py: If True, try to get the Python field type and default value.
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
        self.description: str = parse_para(element.find("briefdescription"))
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
        If True, this type is mutable in Python and needs a None default value.
        """
        self.is_mutable_type: bool = self.cs_field_type in Field.CS_MUTABLE_TYPES
        if field_type in PY_TYPES:
            """:field
            The field's Python type.
            """
            self.py_field_type: str = field_type
        # An enum expressed as a string.
        elif self.cs_field_type in STRS:
            self.py_field_type = "str"
        elif not py:
            self.py_field_type = ""
        else:
            try:
                self.py_field_type = CS_TO_PY_TYPES[field_type]
            except KeyError as e:
                print("Invalid key:", field_type, self.name)
                raise e
        """:field
        If True, the field type is a collection (list, dictionary, etc.).
        """
        self.is_collection: bool = self.cs_field_type.startswith("List<") or self.cs_field_type.startswith("Dictionary<") or self.cs_field_type.endswith("[]")
        # Convert the default value from C# to Python.
        initializer = element.find("initializer")
        if initializer is None:
            """:field
            The default value in the original C# code. Can be None.
            """
            self.cs_default_value: Optional[str] = None
            """:field
            The default value in the code-genned Python code. Can be None.
            """
            self.py_default_value: Optional[str] = None
        else:
            self.cs_default_value: str = initializer.text.split("=")[1].strip()
            if self.py_field_type == "ERROR":
                self.py_default_value = None
            # Dictionary.
            if self.cs_default_value == "new Dictionary<":
                self.cs_default_value = parse_ref(initializer).replace("&gt;", ">").replace("< ", "<").split("=")[1].strip()
            # Array.
            elif self.cs_default_value == "new":
                self.cs_default_value = parse_ref(initializer).split("=")[1].strip()
            if self.cs_field_type in STRS and self.cs_default_value is not None:
                cs_default_value_split = self.cs_default_value.split(".")
                if cs_default_value_split[0] in STRS:
                    self.py_default_value = f'"{cs_default_value_split[1]}"'
                elif self.cs_field_type in Field.CS_ENUM_DEFAULTS:
                    self.py_default_value = Field.CS_ENUM_DEFAULTS[self.cs_field_type]
                else:
                    raise Exception(self.name, self.cs_field_type, self.cs_default_value)
            # Remove the f from the end of the float value.
            elif field_type == "float" and self.cs_default_value.endswith("f"):
                self.py_default_value = self.cs_default_value[:-1]
            elif field_type == "bool":
                self.py_default_value = self.cs_default_value.title()
            elif field_type in PY_TYPES:
                self.py_default_value = self.cs_default_value
            elif self.cs_default_value == "null":
                self.py_default_value = "None"
            # Remove doxygen quotes.
            elif self.py_field_type == "str":
                self.py_default_value = Field.RE_QUOT.sub(r'"\1"', self.cs_default_value)
            # Remove doxygen quotes.
            elif self.py_field_type == "List[str]":
                if "&quot;" in self.cs_default_value:
                    self.py_default_value = '[' + ', '.join(['"' + v + '"' for v in Field.RE_QUOT.findall(self.cs_default_value)]) + ']'
                else:
                    self.py_default_value = '[' + ', '.join(['"' + v + '"' for v in Field.RE_QUOTES.findall(self.cs_default_value)]) + ']'
            elif self.py_field_type == "List[float]" or self.py_field_type == "List[int]":
                self.py_default_value = '[' + ', '.join(Field.RE_NUMBERS.findall(self.cs_default_value)) + ']'
            elif self.py_field_type == "List[bool]":
                self.py_default_value = '[' + ', '.join([v.title() for v in Field.RE_BOOL.findall(self.cs_default_value)]) + ']'
            elif self.cs_default_value in CS_TO_PY_DEFAULT_VALUES:
                self.py_default_value = CS_TO_PY_DEFAULT_VALUES[self.cs_default_value][:]
            elif self.cs_default_value.startswith("new Vector") and "[0]" not in self.cs_default_value:
                # Get the numbers. Ignore the first number because it's, for example, the 3 in Vector3.
                values = Field.RE_NUMBERS.findall(self.cs_default_value)[1:]
                coordinates = list()
                for coordinate, value in zip(["x", "y", "z"], values):
                    coordinates.append('"' + coordinate + '": ' + value)
                self.py_default_value = "{" + ", ".join(coordinates) + "}"
            elif self.cs_default_value.startswith("new Color"):
                values = Field.RE_NUMBERS.findall(self.cs_default_value)
                # Add the implicit alpha value.
                if len(values) == 3:
                    values.append(1)
                coordinates = list()
                for coordinate, value in zip(["r", "g", "b", "a"], values):
                    coordinates.append('"' + coordinate + '": ' + value)
                self.py_default_value = "{" + ", ".join(coordinates) + "}"
            # Zero-vector.
            elif self.cs_default_value.endswith(".zero"):
                num_coordinates = int(re.search(r"(\d+)", self.cs_default_value).group(1))
                coordinates = list()
                for coordinate in ["x", "y", "z"][:num_coordinates]:
                    coordinates.append('"' + coordinate + '": 0')
                self.py_default_value = "{" + ", ".join(coordinates) + "}"
            # A list of vectors or colors.
            elif self.py_field_type == 'List[Dict[str, float]]':
                self.py_default_value = "list()"
                py_vectors = list()
                for vector_type in ["Vector2", "Vector2Int", "Vector3", "Vector3Int", "Color"]:
                    vectors = re.findall(vector_type + r"\((.*?)\)", self.cs_default_value)
                    if len(vectors) > 0:
                        for vector in vectors:
                            values = Field.RE_NUMBERS.findall(vector)
                            coordinates = list()
                            # A vector.
                            if vector_type.startswith("Vector"):
                                for coordinate, value in zip(["x", "y", "z"], values):
                                    coordinates.append('"' + coordinate + '": ' + value)
                                py_vectors.append("{" + ", ".join(coordinates) + "}")
                            # A color.
                            else:
                                if len(values) == 3:
                                    values.append(1)
                                coordinates = list()
                                for coordinate, value in zip(["r", "g", "b", "a"], values):
                                    coordinates.append('"' + coordinate + '": ' + value)
                                py_vectors.append("{" + ", ".join(coordinates) + "}")
                        self.py_default_value = "[" + ", ".join(py_vectors) + "]"
                        break
            elif self.py_field_type == "List[CardinalDirection]":
                directions = re.findall(r"CardinalDirection\.(\w+)", self.cs_default_value)
                self.py_default_value = "[" + ", ".join([f"CardinalDirection.{d}" for d in directions]) + "]"
            elif self.py_field_type == "TrialStatus":
                self.py_default_value = None
            # An empty dictionary.
            elif Field.RE_NEW_DICTIONARY.match(self.cs_default_value) is not None:
                self.py_default_value = "dict()"
            elif Field.RE_NEW_ARRAY.match(self.cs_default_value) is not None:
                self.py_default_value = "list()"
            elif not py:
                self.py_default_value = None
            else:
                raise Exception(self.name, self.py_field_type, self.cs_default_value)
            if self.name == "max_retries" and self.cs_default_value == "":
                self.cs_default_value = 'Req.DEFAULT_MAX_RETRIES'
                self.py_default_value = '100'
            if self.name == "timeout" and self.cs_default_value == "":
                self.cs_default_value = 'Req.DEFAULT_TIMEOUT'
                self.py_default_value = '1000'
            if "_" in self.cs_default_value and '"' not in self.cs_default_value:
                for r in Field.CONST_REPLACEMENTS:
                    if self.py_default_value is not None:
                        self.py_default_value = self.py_default_value.replace(r, Field.CONST_REPLACEMENTS[r])
