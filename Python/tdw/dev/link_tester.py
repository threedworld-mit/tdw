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

    @staticmethod
    def test(directory: str) -> Dict[str, List[str]]:
        """
        :param directory: The root directory.

        :return: A dictionary: Key = File path. Value = A list of bad links.
        """

        # Source: https://stackoverflow.com/a/37462442
        md_link = re.compile(r'\[(.*?)]\((.*?)\)')
        files_with_bad_links: Dict[str, List[str]] = dict()
        ok = ['http://trac.ffmpeg.org/wiki/Encode/H.264',
              'http://obi.virtualmethodstudio.com/tutorials/emittermaterials.html',
              'http://obi.virtualmethodstudio.com/manual/6.3/particlediffusion.html',
              'http://obi.virtualmethodstudio.com/tutorials/clothsetup.html']
        for root_dir, dirs, files in walk(directory):
            for f in files:
                # Only test markdown files.
                if not f.endswith(".md"):
                    continue
                path = Path(root_dir).joinpath(f)
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError as e:
                    print(f)
                    raise e
                md_links = md_link.findall(text)
                md_links: List[str] = [m[1] for m in md_links]
                bad_links: List[str] = []
                for m in md_links:
                    if m in ok:
                        continue
                    if m.startswith("http"):
                        try:
                            resp = head(m)
                            if resp.status_code != 200:
                                print(m, resp.status_code)
                                bad_links.append(m)
                        except:
                            bad_links.append(m)
                    elif m.endswith(".md"):
                        link_path = path.parent.joinpath(m).absolute().resolve()
                        if not link_path.exists():
                            bad_links.append(str(link_path).replace("\\", "/"))
                if len(bad_links) > 0:
                    print(f, bad_links)
                files_with_bad_links[str(path.resolve()).replace("\\", "/")] = bad_links
        return files_with_bad_links


if __name__ == "__main__":
    result = LinkTester.test(str(Config().tdw_docs_path.joinpath("docs")))
    print(dumps(result, indent=2, sort_keys=True))
