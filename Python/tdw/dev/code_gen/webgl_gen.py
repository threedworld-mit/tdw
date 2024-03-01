from typing import List, Dict
from pathlib import Path
import inflection
from tdw.dev.config import Config
from tdw.dev.code_gen.cs_xml.assembly import Assembly
from tdw.dev.code_gen.cs_xml.namespace import Namespace
from tdw.dev.code_gen.cs_xml.enum_type import EnumType
from tdw.dev.code_gen.cs_xml.util import recreate_directory
from tdw.dev.code_gen.py import struct_py, enum_py


class WebGlGen:
    """
    Generate WebGL code and documentation.

    - Generate Python classes for Trials, TrialMessage, and TrialAdders.
    - Generate Python and C# API documentation.
    """

    """:class_var
    Config data.
    """
    CONFIG = Config()
    """:class_var
    Don't generate documentation for these types.
    """
    EXCLUDED_TYPES: List[str] = ["Config", "TrialManager", "NetworkMode", "NativeBindings", "CommandHelpers"]

    @staticmethod
    def namespace_py(namespace: Namespace, enums: Dict[str, EnumType]) -> None:
        """
        C# to Python enum code-gen.

        :param namespace: The namespace definition.
        :param enums: The assembly's enums.
        """

        for enum in namespace.enums:
            if enum.name in WebGlGen.EXCLUDED_TYPES:
                continue
            enum.get_py_doc()
            enum_py(enum)
        for struct in namespace.structs:
            struct.get_py_doc(enums)
            struct_py(struct)
        for klass in namespace.klasses:
            if klass.name in WebGlGen.EXCLUDED_TYPES:
                continue
            klass.get_py_doc(enums)
            struct_py(klass)
        WebGlGen.write_init("trials")
        WebGlGen.write_init("trial_adders")

    @staticmethod
    def assembly_py(assembly: Assembly) -> None:
        """
        Generate WebGL Python classes.

        :param assembly: The assembly.
        """

        for namespace in ["TDW::WebGL", "TDW::WebGL::Trials", "TDW::WebGL::Trials::Tests", "TDW::WebGL::TrialAdders"]:
            WebGlGen.namespace_py(assembly.namespaces[namespace], assembly.enums)

    @staticmethod
    def write_py_docs(assembly: Assembly) -> None:
        """
        Generate WebGL Python documentation.

        :param assembly: The assembly.
        """

        # Get the root output directory.
        root_directory = WebGlGen.CONFIG.tdw_docs_path.joinpath("docs/webgl/py/api").resolve()
        recreate_directory(root_directory)
        # Write the TrialMessage.
        webgl = assembly.namespaces["TDW::WebGL"]
        trial_message = [c for c in webgl.klasses if c.name == "TrialMessage"][0]
        root_directory.joinpath("trial_message.md").write_text(trial_message.get_py_doc(assembly.enums))
        # Write the TrialStatus.
        trial_status = [e for e in webgl.enums if e.name == "TrialStatus"][0]
        root_directory.joinpath("trial_status.md").write_text(trial_status.get_py_doc())
        # Write the trials.
        WebGlGen.write_py_doc_directory(assembly=assembly,
                                        namespace="TDW::WebGL::Trials",
                                        root_directory=root_directory,
                                        folder="trials")
        # Write the tests.
        WebGlGen.write_py_doc_directory(assembly=assembly,
                                        namespace="TDW::WebGL::Trials::Tests",
                                        root_directory=root_directory.joinpath("trials"),
                                        folder="tests")
        # Write the trial adders.
        WebGlGen.write_py_doc_directory(assembly=assembly,
                                        namespace="TDW::WebGL::TrialAdders",
                                        root_directory=root_directory,
                                        folder="trial_adders")

    @staticmethod
    def write_cs_docs(assembly: Assembly) -> None:
        """
        Generate WebGL C# documentation.

        :param assembly: The assembly.
        """

        # Get the root output directory.
        root_directory = WebGlGen.CONFIG.tdw_docs_path.joinpath("docs/webgl/cs/api").resolve()
        recreate_directory(root_directory)
        # Write CommandHelpers.
        webgl = assembly.namespaces["TDW::WebGL"]
        trial_status = [c for c in webgl.klasses if c.name == "CommandHelpers"][0]
        root_directory.joinpath("command_helpers.md").write_text(trial_status.get_cs_doc(methods=True,
                                                                                         enums=assembly.enums,
                                                                                         static=True))
        # Write the TrialStatus.
        trial_status = [e for e in webgl.enums if e.name == "TrialStatus"][0]
        root_directory.joinpath("trial_status.md").write_text(trial_status.get_cs_doc())
        # Write the trials.
        WebGlGen.write_cs_doc_directory(assembly=assembly,
                                        namespace="TDW::WebGL::Trials",
                                        root_directory=root_directory,
                                        folder="trials")
        # Write the add-ons.
        WebGlGen.write_cs_doc_directory(assembly=assembly,
                                        namespace="TDW::WebGL::Trials::AddOns",
                                        root_directory=root_directory,
                                        folder="add_ons")

    @staticmethod
    def write_py_doc_directory(assembly: Assembly, namespace: str, root_directory: Path, folder: str) -> None:
        """
        Generate documentation for a directory of code-genned Python classes.

        :param assembly: The assembly.
        :param namespace: The namespace.
        :param root_directory: The root documentation directory.
        :param folder: The folder name.
        """

        namespace = assembly.namespaces[namespace]
        directory = root_directory.joinpath(folder)
        toc = f"# {inflection.camelize(folder)}\n\n"
        toc_rows = []
        if not directory.exists():
            directory.mkdir(parents=True)
        for k in namespace.klasses:
            if k.abstract:
                continue
            filename = f"{inflection.underscore(k.name)}.md"
            directory.joinpath(filename).write_text(k.get_py_doc(enums=assembly.enums))
            toc_rows.append(f"- [{k.name}]({folder}/{filename})")
        toc += "\n".join(toc_rows)
        root_directory.joinpath(f"{folder}.md").write_text(toc)

    @staticmethod
    def write_cs_doc_directory(assembly: Assembly, namespace: str, root_directory: Path, folder: str) -> None:
        """
        Generate documentation for a directory of C# classes.

        :param assembly: The assembly.
        :param namespace: The namespace.
        :param root_directory: The root documentation directory.
        :param folder: The folder name.
        """

        namespace = assembly.namespaces[namespace]
        directory = root_directory.joinpath(folder)
        toc = f"# {inflection.camelize(folder)}\n\n"
        toc_rows = []
        if not directory.exists():
            directory.mkdir(parents=True)
        for k in namespace.klasses:
            filename = f"{inflection.underscore(k.name)}.md"
            directory.joinpath(filename).write_text(k.get_cs_doc(methods=False, enums=assembly.enums))
            toc_rows.append(f"- [{k.name}]({folder}/{filename})")
        toc += "\n".join(toc_rows)
        root_directory.joinpath(f"{folder}.md").write_text(toc)

    @staticmethod
    def write_init(folder: str) -> None:
        """
        Generate a Python init file.

        :param folder: The folder name.
        """

        root_directory = WebGlGen.CONFIG.tdw_path.joinpath(f"Python/tdw/webgl/{folder}").resolve()
        inits = []
        for f in root_directory.iterdir():
            if f.is_file() and f.stem != "__init__":
                inits.append(f"from .{f.stem} import {inflection.camelize(f.stem, uppercase_first_letter=True)}")
        root_directory.joinpath("__init__.py").write_text("\n".join(inits))


if __name__ == "__main__":
    a = Assembly()
    WebGlGen.assembly_py(a)
    WebGlGen.write_py_docs(a)
    WebGlGen.write_cs_docs(a)
