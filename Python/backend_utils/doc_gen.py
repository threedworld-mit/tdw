from os import walk, chdir
from pathlib import Path
from md_link_tester.md_link_tester import MdLinkTester
from git import Repo
from requests import head
from tdw.dev.config import Config
from tdw.dev.code_gen.cs_xml.assembly import Assembly
from tdw.dev.code_gen.commands_code_gen import CommandsCodeGen
from tdw.dev.code_gen.cached_objects import CachedObjects
from tdw.dev.code_gen.fb_doc_gen import FbDocGen
from tdw.dev.code_gen.py_doc_gen import PyDocGen


"""
Generate code documentation for the TDWBase and tdw repos.
"""

if __name__ == "__main__":
    # Run doxygen and get the assembly data.
    assembly = Assembly()
    # Generate command classes and documentation.
    CommandsCodeGen.generate_commands(assembly)
    # Generate cached objects documentation.
    CachedObjects.generate(assembly)
    # Generate output data documentation.
    FbDocGen.generate()
    # Generate Python API documentation.
    PyDocGen.generate()

    # Test documentation URLs.
    print("Testing all documentation links...")
    md_link_tester = MdLinkTester()
    config = Config()
    # Test the README
    bad_links = md_link_tester.test_file(path=config.tdw_path.joinpath("README.md"))
    if len(bad_links) > 0:
        print("README.md")
        for bad_link in bad_links:
            print("\t", bad_link)
    documentation_path = config.tdw_docs_path.joinpath("docs")
    ignore_files = []
    branch_name = Repo(path=str(config.tdw_path.resolve())).active_branch.name
    ignore_links = []
    for r, ds, fs in walk(str(documentation_path.resolve())):
        for f in fs:
            if not f.endswith(".md") or f in ignore_files:
                continue
            p = Path(r).joinpath(f)
            chdir(str(p.parent.resolve()))
            bad_links_temp = md_link_tester.test_file(f)
            if branch_name != "master":
                bad_links = list()
                for bad_link in bad_links_temp:
                    if "example_controllers" in bad_link:
                        bad_link = bad_link.replace("blob/master", f"blob/{branch_name}")
                        resp = head(bad_link).status_code
                        if resp != 200:
                            bad_links.append(bad_link)
                    else:
                        bad_links.append(bad_link)
            else:
                bad_links = bad_links_temp
            bad_links = [bad_link for bad_link in bad_links if bad_link not in ignore_links]
            if len(bad_links) > 0:
                print(p)
                for bad_link in bad_links:
                    print("\t", bad_link)
    print("...Done!")
