import re
from typing import Optional, Dict, List
from tdw.dev.code_gen.cs_xml.field import Field
from tdw.dev.code_gen.cs_xml.util import CS_TO_PY_TYPES, CS_TO_PY_DEFAULT_VALUES, PY_TYPES, STRS


class PyField:
    """
    A field with a Python type and default value.
    """

    """:class_var
    In Python documentation, these types need None default values.
    """
    CS_MUTABLE_TYPES: List[str] = ["Vector3", "Vector3Int", "Vector2", "Vector2Int", "Color", "Quaternion"]
    """:class_var
    A dictionary of constants declared in TDWUnity as keys and valid Python default values as values.
    """
    CONST_REPLACEMENTS: Dict[str, str] = {"DEFAULT_BOUNDS": "10",
                                          "DEFAULT_FRICTION": "0.05",
                                          "DEFAULT_SENSOR_NAME": '"SensorContainer"',
                                          "LightManager.SHADOW_STRENGTH": "0.582",
                                          "Req.DEFAULT_MAX_RETRIES": "100",
                                          "Req.DEFAULT_TIMEOUT": "1000"}
    
    def __init__(self, field: Field):
        """
        :param field: The field.
        """
        
        """:field
        The field.
        """
        self.field: Field = field
        """:field
        If True, this type is mutable in Python and needs a None default value.
        """
        self.is_mutable_type: bool = field.cs_field_type in PyField.CS_MUTABLE_TYPES
        """:field
        The Python field type.
        """
        self.py_field_type: str = ""
        """:field
        The default Python value. Can be None.
        """
        self.py_default_value: Optional[str] = None
        # Get the Python field type.
        # The C# type has a corresponding Python type of the same name.
        if field.cs_field_type in PY_TYPES:
            self.py_field_type: str = field.cs_field_type
            self.py_default_value = field.cs_default_value[:] if isinstance(field.cs_default_value, str) else None
            if field.cs_default_value == "null":
                self.py_default_value = "None"
            elif field.cs_default_value is not None:
                # Remove the f from the end of the float value.
                if field.cs_field_type == "float" and field.cs_default_value.endswith("f"):
                    self.py_default_value = field.cs_default_value[:-1]
                # Convert a C# boolean to a Python boolean.
                elif field.cs_field_type == "bool":
                    self.py_default_value = field.cs_default_value.title()
            if field.cs_default_value in PyField.CONST_REPLACEMENTS:
                self.py_default_value = PyField.CONST_REPLACEMENTS[field.cs_default_value]
            return
        # The C# type an enum that in Pythin is expressed as a string.
        elif field.cs_field_type in STRS:
            self.py_field_type = "str"
        else:
            try:
                # The C# type has a corresponding Python type of a different name.
                self.py_field_type = CS_TO_PY_TYPES[field.cs_field_type]
            except KeyError as e:
                print("Invalid key:", field.cs_field_type, field.name, field.id)
                raise e
        # Get a pre-set Python default value.
        if field.cs_default_value in PyField.CONST_REPLACEMENTS:
            self.py_default_value = PyField.CONST_REPLACEMENTS[field.cs_default_value]
        # There isn't a default value or this is a constant.
        elif field.initializer is not None and not field.constant:
            # The C# field type is expressed as a string in Python and there is no default value.
            if field.cs_field_type in STRS and field.cs_default_value is not None:
                cs_default_value_split = field.cs_default_value.split(".")
                if cs_default_value_split[0] in STRS:
                    self.py_default_value = f'"{cs_default_value_split[1]}"'
                elif field.cs_field_type in Field.CS_ENUM_DEFAULTS:
                    self.py_default_value = Field.CS_ENUM_DEFAULTS[field.cs_field_type]
                else:
                    raise Exception(field.name, field.cs_field_type, field.cs_default_value)
            # Remove the f from the end of the float value.
            elif field.cs_field_type == "float" and field.cs_default_value.endswith("f"):
                self.py_default_value = field.cs_default_value[:-1]
            # Convert a C# boolean to a Python boolean.
            elif field.cs_field_type == "bool":
                self.py_default_value = field.cs_default_value.title()
            elif field.cs_default_value == "null":
                self.py_default_value = "None"
            elif field.cs_field_type == "string":
                self.py_field_type = "str"
                self.py_default_value = field.cs_default_value[:]
            # Get a list.
            elif self.py_field_type == "List[str]":
                self.py_default_value = '[' + ', '.join(
                    ['"' + v + '"' for v in Field.RE_QUOTES.findall(field.cs_default_value)]) + ']'
            elif self.py_field_type == "List[float]" or self.py_field_type == "List[int]":
                self.py_default_value = '[' + ', '.join(Field.RE_NUMBERS.findall(field.cs_default_value)) + ']'
            elif self.py_field_type == "List[bool]":
                self.py_default_value = '[' + ', '.join(
                    [v.title() for v in Field.RE_BOOL.findall(field.cs_default_value)]) + ']'
            elif field.cs_default_value in CS_TO_PY_DEFAULT_VALUES:
                self.py_default_value = CS_TO_PY_DEFAULT_VALUES[field.cs_default_value][:]
            elif field.cs_default_value.startswith("new Vector") and "[0]" not in field.cs_default_value:
                # Get the numbers. Ignore the first number because it's, for example, the 3 in Vector3.
                values = Field.RE_NUMBERS.findall(field.cs_default_value)[1:]
                coordinates = list()
                for coordinate, value in zip(["x", "y", "z"], values):
                    coordinates.append('"' + coordinate + '": ' + value)
                self.py_default_value = "{" + ", ".join(coordinates) + "}"
            elif field.cs_default_value.startswith("new Color"):
                values = Field.RE_NUMBERS.findall(field.cs_default_value)
                # Add the implicit alpha value.
                if len(values) == 3:
                    values.append(1)
                coordinates = list()
                for coordinate, value in zip(["r", "g", "b", "a"], values):
                    coordinates.append('"' + coordinate + '": ' + value)
                self.py_default_value = "{" + ", ".join(coordinates) + "}"
            # Zero-vector.
            elif field.cs_default_value.endswith(".zero"):
                num_coordinates = int(re.search(r"(\d+)", field.cs_default_value).group(1))
                coordinates = list()
                for coordinate in ["x", "y", "z"][:num_coordinates]:
                    coordinates.append('"' + coordinate + '": 0')
                self.py_default_value = "{" + ", ".join(coordinates) + "}"
            # A list of vectors or colors.
            elif self.py_field_type == 'List[Dict[str, float]]':
                self.py_default_value = "list()"
                py_vectors = list()
                for vector_type in ["Vector2", "Vector2Int", "Vector3", "Vector3Int", "Color"]:
                    vectors = re.findall(vector_type + r"\((.*?)\)", field.cs_default_value)
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
                directions = re.findall(r"CardinalDirection\.(\w+)", field.cs_default_value)
                self.py_default_value = "[" + ", ".join([f"CardinalDirection.{d}" for d in directions]) + "]"
            elif self.py_field_type == "TrialStatus":
                self.py_default_value = None
            # An empty dictionary.
            elif Field.RE_NEW_DICTIONARY.match(field.cs_default_value) is not None:
                self.py_default_value = "dict()"
            elif Field.RE_NEW_ARRAY.match(field.cs_default_value) is not None:
                self.py_default_value = "list()"
            else:
                raise Exception(field.name, self.py_field_type, field.cs_default_value)
