from typing import List, Dict
from inflection import underscore
from tdw.dev.config import Config
from tdw.dev.code_gen.cs_xml.util import recreate_directory
from tdw.dev.code_gen.cs_xml.assembly import Assembly
from tdw.dev.code_gen.cs_xml.klass import Klass


class CachedObjects:
    """
    Generate Cached Objects C# documentation.
    """

    @staticmethod
    def generate(assembly: Assembly) -> None:
        """
        Generate the documentation.

        :param assembly: The assembly.
        """

        config = Config()
        documentation_directory = config.tdw_docs_path.joinpath("docs/unity/cached_object_api")
        recreate_directory(documentation_directory)
        klasses: Dict[str, Klass] = {k.id: k for k in assembly.namespaces["TDW"].klasses}
        cached_object_types: List[str] = list()
        # Get all types of CachedObject.
        for k in assembly.namespaces["TDW"].klasses:
            # We need to do this by name rather than class inheritance because of generic types.
            if k.name.startswith("Cached"):
                cached_object_types.append(k.id)
        # Generate the overview doc.
        toc = "# Cached Object API\n\n"
        toc += config.tdw_docs_path.joinpath("docs/unity/cached_object_api_resources/cached_object_api_overview.md").read_text()
        toc += "\n\n![](../cached_object_api_resources/images/cached_objects.png)\n\n***\n\n"
        documentation_directory.joinpath("cached_object_api.md").write_text(toc)
        # Generate the API docs.
        for co in cached_object_types:
            k = klasses[co]
            filename = underscore(k.name) + ".md"
            doc = f"# {k.name}\n\n{k.description}\n\n{k.get_cs_fields_table()}"
            documentation_directory.joinpath(filename).write_text(doc)


if __name__ == "__main__":
    a = Assembly()
    CachedObjects.generate(a)
