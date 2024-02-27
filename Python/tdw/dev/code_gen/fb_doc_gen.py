from os import walk
from typing import Dict, List, Tuple, Optional
import re
from pathlib import Path
from inflection import underscore
from tdw.dev.config import Config


class Field:
    """
    A field in a Flatbuffer object.
    """

    def __init__(self, name, data_type, description, is_array):
        self.name = name
        self.data_type = data_type
        self.is_array = is_array
        self.description = description

    def get_data_type(self):
        """
        Returns the formatted type. If the schema has [int], this returns int[], etc.
        :return:
        """
        if self.is_array:
            return self.data_type + "[]"
        else:
            return self.data_type


class DocObj:
    def __init__(self, name, defs, file_id, desc, parent):
        self.name = name
        self.defs = defs
        self.parent = parent
        self.desc = desc
        self.file_id = file_id

        self.call_example = f"`{self.name.lower()[0]} = {self.name}(byte_array)`"

    def get_header(self):
        return f'## {self.name}\n\n{self.call_example}\n\n**Identifier:** `{self.file_id}`\n\n{self.desc}\n\n' \
            f'| Function | Description | Return type |\n| --- | --- | --- |\n'

    def get_def_descs(self):
        descs = ""
        for q in self.defs:
            descs += f"| `{q[0]}` | {q[1]} | {q[2]} |\n"
        return descs + "\n"


class OutputDataParser:
    """
    Parse a .fbs file.
    """

    CONFIG = Config()
    PY_PATH = CONFIG.tdw_path.joinpath("Python/tdw/output_data.py")

    def __init__(self, filename: str):
        self.name = filename
        self.fbs_path = self.CONFIG.tdwunity_path.joinpath(f"Flatbuffer/OutputData/{filename}.fbs")

    def get_defs(self):
        """
        Returns the Python functions.
        """

        # Get the header.
        header, parent, header_line = self._get_class_header()
        if not header:
            return None, None, None, None

        defs = []
        return_types = []

        txt = self.PY_PATH.read_text()
        lines = txt.split("\n")
        for i in range(header_line + 1, len(lines)):
            if lines[i].startswith("class"):
                return header, parent, defs, return_types
            # Check if this line is def <method>:
            def_match = re.match(r"def (.*):", lines[i].strip())
            if not def_match:
                continue
            # Ignore def get_data(self):
            def_name = re.match(r"def (.*)\(", lines[i].strip()).group(1)
            if def_name == "get_data" or def_name.startswith("_"):
                continue
            # Parse the def.
            the_def = def_match.group(1).strip().replace("(self, ", "(").replace("(self", "(")

            # Remove the return type.
            assert " -> " in the_def, f"No return type: {the_def}"

            def_split = the_def.split(" -> ")
            the_def = def_split[0]
            return_types.append(def_split[1])

            # Remove further type hinting.
            the_def = re.sub(r": (\w+)", "", the_def)

            defs.append(the_def)
        return header, parent, defs, return_types

    def _get_class_header(self) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Get the class header in output_data.py
        """

        # Open the Python script.
        txt = self.PY_PATH.read_text()
        lines = txt.split("\n")
        for line, i in zip(lines, range(len(lines))):
            class_header = re.match(r"class (\w+)", line)
            if not class_header:
                continue
            class_header = class_header.group(1)
            if class_header == self.name:
                parent_re = re.match(r"^class \w+\((.*?)\)", line)
                if parent_re is not None:
                    parent = parent_re.group(1)
                else:
                    parent = "OutputData"
                return class_header, parent, i
        return None, None, None

    def get_schema_fields(self):
        """
        Returns the fields of the schema file.
        """

        fields = dict()
        table_desc = None
        file_id = None

        txt = self.fbs_path.read_text()
        lines = txt.split("\n")
        for fb_type in ["table", "struct"]:
            for line, i in zip(lines, range(len(lines))):
                # Look for the description of a table.
                match = re.match(fb_type + r" (.*)", line)
                if match:
                    # Parse the name of the table and the description.
                    table_name = re.match(fb_type + r" (.*) //", line).group(1)
                    if table_name == self.name:
                        table_desc = line.split("//")[1].strip()
                        file_id = OutputDataParser._get_file_identifer(lines)
                    fields.update(OutputDataParser._get_fields(lines, i))
        return fields, table_desc, file_id

    @staticmethod
    def _get_file_identifer(lines):
        for line in lines:
            if line.startswith("file_identifier"):
                return re.match(r'file_identifier \"(.*)\"', line).group(1)
        return None

    @staticmethod
    def _get_fields(lines, line_num):
        """
        Returns the fields of a table or struct.

        :param lines: All lines in the schema file.
        :param line_num: The line number.
        """

        fields = dict()

        for i in range(line_num + 2, len(lines)):
            if lines[i] == "}":
                return fields
            elif lines[i] == "":
                continue
            # This line contains a field.
            if ":" in lines[i] and ";" in lines[i]:
                # Parse the field name.
                field_name = re.match(r"^(.*?):", lines[i].strip()).group(1)
                # Parse the field type.
                field_type = re.match(field_name + r":(.*);", lines[i].strip()).group(1)
                # If this is an array, parse it correctly.
                if field_type[0] == "[" and field_type[-1] == "]":
                    is_array = True
                    field_type = field_type[1:-1]
                else:
                    is_array = False

                # Try to get the documentation.
                try:
                    assert len(lines[i].split("// ")) >= 2
                    field_desc = lines[i].split("// ")[1].strip()
                except AssertionError:
                    print("Missing comment: " + lines[i])
                    field_desc = ""

                fields.update({field_name: Field(field_name, field_type, field_desc, is_array)})
        return fields


class FbDocGen:
    """
    Generate output data documentation.
    """

    @staticmethod
    def get_inheritance(fb_class: DocObj, all_other) -> DocObj:
        """
        Append def documentation inherited from parent classes to each output data class.

        :param fb_class: The class.
        :param all_other: All other output data classes.
        """

        for a in all_other:
            # Ignore if it's the same.
            if fb_class.file_id == a.file_id:
                continue
            # Append their defs to mine.
            elif fb_class.parent == a.name:
                temp = a.defs[:]
                temp.extend(fb_class.defs)
                fb_class.defs = temp
                # Set a new parent.
                fb_class.parent = a.parent
                # Recurse through inheritance.
                return FbDocGen.get_inheritance(fb_class, all_other)
        return fb_class

    @staticmethod
    def get_commands(config: Config) -> Dict[str, List[str]]:
        """
        :param config: `Config` data.

        :return: A list of file paths to Command C# scripts that send data.
        """

        assets_directory = config.tdwunity_path.joinpath("TDWUnity/Assets")
        commands: Dict[str, List[str]] = dict()
        for folder in ["", "TDWThirdParty"]:
            root_directory = assets_directory.joinpath(folder).joinpath("TDW/Scripts/Networking/Commands/SendDataCommand").resolve()
            for root, dirs, files in walk(str(root_directory)):
                for f in files:
                    if f.endswith("meta"):
                        continue
                    path = Path(root).joinpath(f)
                    text = path.read_text(encoding="utf-8")
                    if "public abstract class" in text:
                        continue
                    tags = re.search(r'doc_gen_tags=(.*)', text, flags=re.MULTILINE).group(1)
                    if "send_data_once" in tags:
                        output_data = [tags.split("send_data_once:")[1]]
                    else:
                        output_data = []
                        for tag in tags.split(","):
                            if tag.startswith("send_data"):
                                output_data.extend(tag.split(":")[1].split(";"))
                    commands[f.split('.')[0]] = output_data
        return commands

    @staticmethod
    def generate() -> None:
        """
        Generate the documentation.
        """

        ini = Config()
        commands = FbDocGen.get_commands(ini)
        root_directory = ini.tdw_path.joinpath("Python/tdw/FBOutput")

        usage_path = ini.tdw_docs_path.joinpath("docs/output_data/usage.md")
        usage = usage_path.read_text()

        doc = f"# Output Data API\n{usage}\n"

        toc = "# Table of Contents\n| Output Data | Command | Description | Identifier |\n| --- | --- | --- | --- |\n"

        datas = dict()

        fast_data = ["AvatarIds", "ObjectIds", "FastAvatars", "FastImageSensors", "FastTransforms"]
        parsers = list()
        # Get output data from Python scripts.
        for f in root_directory.iterdir():
            if not f.is_file():
                continue
            # Ignore the __init__ file and the test Junk data type.
            if f.stem == "__init__" or f.stem == "Junk":
                continue
            parsers.append(OutputDataParser(f.stem))
        # Get fast data.
        for f in ini.tdwunity_path.joinpath("Flatbuffer/OutputData").resolve().iterdir():
            if f.stem in fast_data:
                parsers.append(OutputDataParser(f.stem))
        for o in parsers:
            type_name, type_parent, type_defs, return_types = o.get_defs()

            # If there isn't any class in output_data.py, check if there should be one.
            if not type_name:
                # If there isn't a schema file, then it's not a root object.
                if not o.fbs_path.exists():
                    continue
                try:
                    assert "root_type " not in o.fbs_path.read_text()
                except AssertionError:
                    print(f"Missing output_data.py class for: {o.name}")
                # Ignore this data type and continue.
                continue

            # Get the schema fields
            schema_fields, table_desc, file_id = o.get_schema_fields()
            try:
                assert schema_fields
            except AssertionError:
                print(f"No schema fields for: {type_name}")
                continue

            def_descs = []

            for d, r in zip(type_defs, return_types):
                r = "`" + r + "`"
                # Make sure that the name is formatted correctly.
                desired = re.match(r"get_(.*)\(", d)
                try:
                    assert desired
                except AssertionError:
                    print(f"Bad def name: {d}")
                    continue

                # Get a description of the function.
                desired = desired.group(1)

                # Parse functions that return root-level fields.
                if desired in schema_fields:
                    schema_desc = schema_fields[desired].description
                    def_desc = schema_desc
                    def_descs.append((d, def_desc, r))
                # Parse functions that return fields from objects in an array.
                else:
                    schema_array_fields = [f for f in schema_fields if schema_fields[f].is_array]
                    if desired == "num":
                        if len(schema_array_fields) == 1:
                            def_desc = f"The number of {schema_array_fields[0]}."
                        elif d == "get_num()":
                            def_desc = "The number of objects."
                        else:
                            raise Exception(f"Missing an array: {type_name}")
                    # Try parsing a description of a list.
                    else:
                        desired = desired.replace("angular_velocity", "angularvelocity")
                        desired = desired.replace("pass_mask", "passmask")
                        desired = desired.replace("relative_velocity", "relativevelocity")
                        words = desired.split("_")
                        if o.name == "Transforms" and desired == "position":
                            def_desc = "The position of the object's pivot point, in the order (x, y, z)."
                        elif o.name == "LocalTransforms" and desired == "forward":
                            def_desc = "The forward directional vector, in worldspace rotational coordinates."
                        elif len(words) == 1:
                            def_desc = f"The {words[0]}."
                        elif words[0] == "num":
                            def_desc = "The number of "
                            for i in range(1, len(words)):
                                def_desc += words[i] + " "
                            def_desc = def_desc[:-1] + "."
                        else:
                            if words[-1] == "id":
                                first_word = "ID"
                            else:
                                first_word = words[-1]
                            def_desc = f"The {first_word} of the "
                            for i in range(len(words) - 1):
                                def_desc += words[i] + " "
                            if "position" in desired:
                                def_desc += "in the order of (x, y, z)"
                            if "rotation" in desired:
                                def_desc += "in the order (x, y, z, w)"
                            def_desc = def_desc.strip() + "."
                    def_desc = def_desc.replace("angularvelocity", "angular velocity")
                    def_desc = def_desc.replace("passmask", "pass mask")
                    def_desc = def_desc.replace("relativevelocity", "relative velocity")
                    def_descs.append((d, def_desc, r))

            datas.update({type_name: DocObj(type_name, def_descs, file_id, table_desc, type_parent)})

        # Get inheritance.
        for d in datas:
            datas[d] = FbDocGen.get_inheritance(datas[d], datas.values())

        # Generate the table of contents.
        for command in commands:
            for output_data_name in commands[command]:
                if output_data_name == "Junk":
                    continue
                o = datas[output_data_name]
                toc += f"| [{o.name}](#{o.name}) | [{command}](../command_api/{underscore(command)}.md) | {o.desc} | `{o.file_id}` |\n"
        doc += toc + "\n# API\n"

        for d in datas:
            doc += datas[d].get_header()
            doc += datas[d].get_def_descs()

        output_path = ini.tdw_docs_path.joinpath("docs/output_data/output_data.md")
        output_path.write_text(doc)


if __name__ == "__main__":
    # Test documentation URLs.
    FbDocGen.generate()
