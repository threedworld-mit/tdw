from os import walk
from json import dumps
import re
from typing import List, Dict
from pathlib import Path
from requests import head
from tdw.dev.config import Config


class LinkTester:
    """
    Test all documentation links.
    """

    """:class_var
    Regex pattern for finding markdown links.
    """
    MD_LINK: re.Pattern = re.compile(r'\[(.*?)]\((.*?)\)')
    """:class_var
    These URLs are OK.
    """
    OK: List[str] = ['http://trac.ffmpeg.org/wiki/Encode/H.264',
                     'http://obi.virtualmethodstudio.com/tutorials/emittermaterials.html',
                     'http://obi.virtualmethodstudio.com/manual/6.3/particlediffusion.html',
                     'http://obi.virtualmethodstudio.com/tutorials/clothsetup.html']

    @staticmethod
    def test_directory(directory: str) -> Dict[str, List[str]]:
        """
        :param directory: The root directory.

        :return: A dictionary: Key = File path. Value = A list of bad links.
        """

        # Source: https://stackoverflow.com/a/37462442

        files_with_bad_links: Dict[str, List[str]] = dict()

        for root_dir, dirs, files in walk(directory):
            for f in files:
                # Only test markdown files.
                if not f.endswith(".md"):
                    continue
                path = Path(root_dir).joinpath(f)
                text = path.read_text(encoding='ISO-8859-1')
                bad_links = LinkTester.test_text(text, path)
                if len(bad_links) > 0:
                    files_with_bad_links[str(path.resolve()).replace("\\", "/")] = bad_links
        return files_with_bad_links

    @staticmethod
    def test_text(text: str, path: Path) -> List[str]:
        """
        Test the text of a file.

        :param text: The text of a file.
        :param path: The path to the file.

        :return: A list of bad links.
        """

        md_links = LinkTester.MD_LINK.findall(text)
        md_links: List[str] = [m[1] for m in md_links]
        bad_links: List[str] = []
        for m in md_links:
            if m in LinkTester.OK:
                continue
            if m.startswith("http"):
                try:
                    resp = head(m, timeout=10)
                    if resp.status_code != 200:
                        bad_links.append(m)
                except:
                    bad_links.append(m)
            elif m.endswith(".md"):
                link_path = path.parent.joinpath(m).absolute().resolve()
                if not link_path.exists():
                    bad_links.append(str(link_path).replace("\\", "/"))
        return bad_links


if __name__ == "__main__":
    result = LinkTester.test_directory(str(Config().tdw_docs_path.joinpath("docs")))
    print(dumps(result, indent=2, sort_keys=True))
