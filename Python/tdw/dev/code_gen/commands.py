from typing import List, Dict
import re
from inflection import underscore
from tdw.dev.config import Config
from tdw.dev.cs_xml.assembly import Assembly
from tdw.dev.cs_xml.util import COMMAND_TAGS, recreate_directory
from tdw.dev.code_gen.py import struct_py


def generate_commands(assembly: Assembly) -> None:
    """
    Generate Python classes of each command and Python/JSON/C# documentation of each command.

    :param assembly: The TDW assembly.
    """

    config = Config()
    # Set the output directories.
    python_commands_directory = config.tdw_path.joinpath("Python/tdw/commands").resolve()
    recreate_directory(python_commands_directory)
    documentation_directory = config.tdw_docs_path.joinpath("docs/command_api")
    recreate_directory(documentation_directory)
    # Get all enums in the assembly.
    enums = assembly.get_enum_types()
    klass_docs: Dict[str, List[str]] = dict()
    abs_docs: Dict[str, str] = dict()
    abs_parents: Dict[str, str] = dict()
    klass_descs: Dict[str, str] = dict()
    inits = []
    # Get abstract class descriptions.
    for k in assembly.namespaces["TDWInput"].klasses:
        if not k.is_command:
            continue
        if k.abstract:
            abs_docs[k.name] = k.description
            klass_docs[k.name] = list()
            abs_parents[k.name] = k.parent
    for k in assembly.namespaces["TDWInput"].klasses:
        if not k.is_command:
            continue
        # Generate the Python class.
        struct_py(k)
        if k.abstract:
            continue
        inits.append(f'from .{underscore(k.name)} import {k.name}')
        command_tags = []
        if "doc_gen_tags" in k.description:
            split = k.description.split("doc_gen_tags")
            description = split[0].strip()
            tags = split[1].split("=")[1].split(",")
            for tag_key in tags:
                split = tag_key.split(":")
                v = COMMAND_TAGS[split[0]]
                tag_description = v["description"][:]
                if "?" in tag_description:
                    if split[0] == "send_data" or split[0] == "send_data_once":
                        tag_description = tag_description.replace("?", f"[`{split[1]}`](../output_data/{underscore(split[1])}.md)")
                    else:
                        tag_description = tag_description.replace("?", split[1])
                tag = f"- **{v['title']}:** {tag_description}"
                command_tags.append(tag)
        else:
            description = k.description
        doc = f"# {k.name}\n\n{description}\n\n" + "\n".join(command_tags)
        if len(command_tags) > 0:
            doc += "\n\n"
        json = k.get_json_doc(enums)
        py = re.match(r"# \w+\n\n((.|\n)*)", k.get_py_doc(enums), flags=re.MULTILINE).group(1).replace(description, "").strip()
        doc += (f"## Python\n\n{py}\n\nIn Python, you can declare commands as either Python objects or as JSON dictionaries. "
                "Whenever possible, you should opt for declared objects to prevent potential bugs. "
                "Until TDW 2.0, commands could only be declared as JSON dictionaries. "
                f"We have kept this feature in TDW to support legacy projects.\n\n{json}\n\n***\n\n")
        cs = re.match(r"# \w+\n\n((.|\n)*)", k.get_cs_doc(methods=False, enums=enums),
                      flags=re.MULTILINE).group(1).replace(k.description, "").strip()
        doc += f"## C#\n\nThis C# code can only be used in the context of a C# `Trial` subclass.\n\n{cs}"
        klass_docs[k.parent].append(k.name)
        klass_descs[k.name] = description
        # Write the documentation.
        documentation_directory.joinpath(f"{underscore(k.name)}.md").write_text(doc)
    # Build the table of contents.
    checked = []
    num_abs = len(abs_docs)
    to_check = ["Command"]
    toc = "# Command API\n\n"
    while len(checked) < num_abs:
        while len(to_check) > 0:
            abs_command = to_check.pop(0)
            # Add the header.
            toc += f"#### {abs_command}\n\n{abs_docs[abs_command]}\n\n"
            # Add the children.
            children = [f"| [{child}]({underscore(child)}.md) | {klass_descs[child].split('.')[0]}. |" for child in klass_docs[abs_command]]
            if len(children) > 0:
                toc += "| Command | Description |\n| --- | --- |\n"
                toc += "\n".join(children) + "\n\n"
            # Mark as checked.
            checked.append(abs_command)
            # Add children.
            abs_children = [k for k in abs_parents if abs_parents[k] is not None and abs_parents[k] == abs_command]
            abs_children.reverse()
            for c in abs_children:
                to_check.insert(0, c)
    documentation_directory.joinpath("command_api.md").write_text(toc)
    # Generate the init file.
    python_commands_directory.joinpath("__init__.py").write_text("\n".join(inits))


if __name__ == "__main__":
    generate_commands(Assembly())
