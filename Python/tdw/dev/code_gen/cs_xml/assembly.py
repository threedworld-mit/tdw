from os import chdir, getcwd
from copy import copy
from xml.etree import ElementTree as Et
from pathlib import Path
from subprocess import call, DEVNULL
from typing import List, Dict
from shutil import rmtree
from tdw.dev.code_gen.cs_xml.util import XML_DIRECTORY, get_root
from tdw.dev.code_gen.cs_xml.namespace import Namespace
from tdw.dev.code_gen.cs_xml.struct import Struct
from tdw.dev.code_gen.cs_xml.klass import Klass
from tdw.dev.code_gen.cs_xml.enum_type import EnumType, enums_from_struct_xml


class Assembly:
    """
    A collection of namespaces in a common assembly.

    This requires doxygen to be installed on your computer.
    """

    """:class_var
    Generate data only for members of these namespaces.
    """
    NAMESPACES: List[str] = ["TDW::WebGL", "TDW::WebGL::Trials", "TDW::WebGL::Trials::Tests",
                             "TDW::WebGL::TrialAdders", "TDW::WebGL::Trials::AddOns", "TDWInput"]
    """:class_var
    Ignore this struct type.
    """
    IGNORE: List[str] = ["Config"]

    def __init__(self, delete_xml: bool = True):
        # Run doxygen.
        xml_directory = Path(XML_DIRECTORY)
        if not xml_directory.exists():
            # Generate doxygen code.
            cwd = getcwd()
            chdir(xml_directory.parent)
            print("Running doxygen...")
            call(["doxygen", "DoxyFile"], stdout=DEVNULL, stderr=DEVNULL)
            print("...done!")
            chdir(cwd)
        structs: List[Struct] = list()
        klasses: List[Klass] = list()
        tdw_enums: List[EnumType] = list()
        namespace_paths: List[Path] = list()
        for f in xml_directory.iterdir():
            # Ignore these files.
            if not f.is_file() or "8cs" in f.name or f.suffix != ".xml":
                continue
            # Check if this is a struct, enum, or class.
            root: Et.ElementTree = get_root(f.name)
            compound_def = root.find("compounddef")
            if compound_def is None:
                continue
            kind_def = compound_def.attrib["kind"]
            if kind_def == "dir":
                continue
            # Ignore anything that isn't public.
            if "prot" in compound_def.attrib and compound_def.attrib["prot"] != "public":
                continue
            # This is a class, struct, or namespace.
            if kind_def == "class" or kind_def == "struct" or kind_def == "namespace":
                compound_name: Et.Element = compound_def.find("compoundname")
                # Ignore types that aren't in any namespace.
                if (kind_def == "class" or kind_def == "struct") and "::" not in compound_name.text:
                    continue
                # Ignore certain types.
                if "::" in compound_name.text and compound_name.text.split("::")[-1] in Assembly.IGNORE:
                    continue
                # Ignore anything in the wrong namespace.
                if compound_name is not None:
                    namespace_split = compound_name.text.split("::")
                    if compound_name.text == "TDW::WebGL" or len(namespace_split) == 1:
                        namespace_name = compound_name.text
                    else:
                        namespace_name = "::".join(namespace_split[:-1])
                    if namespace_name == "TDW" and (kind_def == "class" or kind_def == "struct"):
                        tdw_enums.extend(enums_from_struct_xml(element=get_root(f.name).find("compounddef")))
                    if kind_def == "namespace":
                        namespace_paths.append(f)
                    if namespace_name not in Assembly.NAMESPACES:
                        continue
                    # Add the file path to the list of classes or structs.
                    if kind_def == "class" and namespace_name != "TDW":
                        klasses.append(Klass(element=get_root(f.name).find("compounddef")))
                    elif kind_def == "struct" and namespace_name != "TDW":
                        structs.append(Struct(element=get_root(f.name).find("compounddef")))
        # Inherit fields.
        inheritance: List[Klass] = list()
        for i in range(len(klasses)):
            Assembly.set_class_inheritance_children(klasses[i], klasses, inheritance)
        for i in range(len(inheritance)):
            Assembly.set_class_inheritance_parents(inheritance[i], klasses)
        klasses = inheritance
        """:field
        A dictionary of each namespace in the assembly.
        """
        self.namespaces: Dict[str, Namespace] = dict()
        for f in namespace_paths:
            namespace = Namespace(f.name, structs, klasses)
            # Add enums.
            if namespace.name == "TDW":
                namespace.enums.extend(tdw_enums)
            # Add the namespace.
            self.namespaces[namespace.name] = namespace
        # Remove the XML.
        if delete_xml:
            rmtree(str(xml_directory))
            
    def get_enum_types(self) -> Dict[str, EnumType]:
        """
        :return: A dictionary of all enum types in the assembly.
        """

        enums: Dict[str, EnumType] = dict()
        for namespace in self.namespaces.values():
            for enum in namespace.enums:
                enums[enum.name] = enum
            for klass in namespace.klasses:
                for enum in klass.enums:
                    enums[enum.name] = enum
        return enums

    def get_enum_tables(self) -> Dict[str, str]:
        """
        :return: A dictionary. Keys: The name of each enum in the assembly. Values: String tables of enum values.
        """

        return {k: v[k].get_table() for (k, v) in self.get_enum_types().items()}

    @staticmethod
    def set_class_inheritance_children(klass: Klass, klasses: List[Klass], inheritance: List[Klass]) -> None:
        """
        Iterate through each class to find this class's inherited fields and methods.

        :param klass: The class.
        :param klasses: All classes in the assembly.
        :param inheritance: This class's inheritance chain.
        """

        replaced = False
        for i in range(len(inheritance)):
            if inheritance[i].name == klass.name:
                inheritance[i] = klass
                replaced = True
                break
        if not replaced:
            inheritance.append(klass)
        for child_id in klass.child_ids:
            for cl in klasses:
                field_ids = [f.id for f in cl.inherited_fields]
                if child_id == cl.id:
                    fields = klass.fields[:]
                    fields.extend(klass.inherited_fields)
                    for field in fields:
                        if field.id in field_ids:
                            continue
                        cl.inherited_fields.append(copy(field))
                    if cl.name == "Command":
                        klass.is_command = True
                    Assembly.set_class_inheritance_children(cl, klasses, inheritance)

    @staticmethod
    def set_class_inheritance_parents(klass: Klass, klasses: List[Klass]) -> None:
        """
        Sometimes, doxygen gives us a child class's parents but not vice versa.
        We need to run this method to get the child class's heritage.

        :param klass: The class.
        :param klasses: This class's inheritance chain.
        """

        # Copy the root parent ID.
        parent_id = copy(klass.parent_id)
        # Get all the class's fields.
        field_ids = [f.id for f in klass.fields]
        field_ids.extend([f.id for f in klass.inherited_fields])
        # Loop until we're at a root class.
        while parent_id is not None:
            # Get the parent class.
            cl = [k for k in klasses if k.id == parent_id][0]
            # Inherit the fields.
            fields = cl.fields[:]
            fields.extend(cl.inherited_fields)
            for field in fields:
                if field.id in field_ids:
                    continue
                klass.inherited_fields.append(copy(field))
                field_ids.append(field.id)
            # Set the parent.
            parent_id = copy(cl.parent_id)
            if cl.name == "Command":
                klass.is_command = True
