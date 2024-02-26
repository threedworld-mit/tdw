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
        # Set the output directory.
        documentation_directory = config.tdw_docs_path.joinpath("docs/unity/cached_object_api")
        recreate_directory(documentation_directory)
        klasses: Dict[str, Klass] = {k.id: k for k in assembly.namespaces["TDW"].klasses}
        cached_object_types: List[str] = list()
        for k in assembly.namespaces["TDW"].klasses:
            if k.name == "CachedObjectBase":
                CachedObjects.get_cached_object_types(kid=k.id, cached_object_types=cached_object_types, klasses=klasses)
                break
        toc = ("# Cached Object API\n\n"
               "In TDW, Cached Objects are C# data structures that store data such as object IDs and GameObjects.\n\n"
               "![](../images/cached_objects.png)\n\n***\n\n")
        links = []
        for co in cached_object_types:
            k = klasses[co]
            filename = underscore(k.name) + ".md"
            links.append(f"- [{k.name}]({filename})\n")
            doc = f"# {k.name}\n\n{k.description}\n\n{k.get_cs_fields_table()}"
            documentation_directory.joinpath(filename).write_text(doc)
        toc += "\n".join(links)
        documentation_directory.joinpath("cached_object_api.md").write_text(toc)

    @staticmethod
    def get_cached_object_types(kid: str, cached_object_types: List[str], klasses: Dict[str, Klass]) -> None:
        co = klasses[kid]
        for child_id in co.child_ids:
            cached_object_types.append(child_id)
            CachedObjects.get_cached_object_types(child_id, cached_object_types, klasses)


if __name__ == "__main__":
    a = Assembly()
    CachedObjects.generate(a)
