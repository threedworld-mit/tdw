from argparse import ArgumentParser
from json import dumps
from tdw.dev.config import Config
from tdw.dev.link_tester import LinkTester
from tdw.dev.code_gen.cs_xml.assembly import Assembly
from tdw.dev.code_gen.commands_gen import CommandsGen
from tdw.dev.code_gen.cached_objects import CachedObjects
from tdw.dev.code_gen.fb_doc_gen import FbDocGen
from tdw.dev.code_gen.py_doc_gen import PyDocGen
from tdw.dev.code_gen.webgl_gen import WebGlGen


"""
Generate code documentation for the TDWBase and tdw repos.
"""

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--links", action="store_true", help="Test all local links and URLs")
    args = parser.parse_args()
    # Run doxygen and get the assembly data.
    assembly = Assembly()
    print("Generating code and docs...")
    # Generate command classes and documentation.
    CommandsGen.generate(assembly)
    # Generate cached objects documentation.
    CachedObjects.generate(assembly)
    # Generate WebGL classes and documentation.
    WebGlGen.assembly_py(assembly)
    WebGlGen.write_py_docs(assembly)
    WebGlGen.write_cs_docs(assembly)
    # Generate output data documentation.
    FbDocGen.generate()
    # Generate Python API documentation.
    PyDocGen.generate()
    print("...Done!")

    # Test documentation URLs.
    if args.links:
        print("Testing all documentation links...")
        bad_links = LinkTester.test_directory(str(Config().tdw_docs_path.joinpath("docs")))
        if len(bad_links) > 0:
            print(dumps(bad_links, indent=2, sort_keys=True))
        print("...Done!")
