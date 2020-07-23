from typing import List
from subprocess import Popen, PIPE, check_output
from requests import get, head
import zipfile
from pathlib import Path
import re
from platform import system
from distutils import dir_util
from tdw.backend.platforms import SYSTEM_TO_RELEASE
from tdw.backend.paths import BUILD_ROOT_DIR

__version__ = "1.6.1"


class BuildVersion:
    """
    Get the version of the build and the release file.
    """

    def __init__(self, version: str = __version__[:]):
        """
        :param version: The version to download.
        """

        self.version = version
        self.url = f"https://github.com/threedworld-mit/tdw/releases/download/v{self.version}/" \
                   f"{SYSTEM_TO_RELEASE[system()]}.zip"
        if BUILD_ROOT_DIR.exists():
            print("Deleted old build.")
            dir_util.remove_tree(str(BUILD_ROOT_DIR.resolve()))

    def download_and_unzip(self) -> bool:
        """
        Download the release corresponding to this version. Move it to the build path and extract it.

        :return: True if the build downloaded.
        """

        # Check if the build exists.
        if head(self.url).status_code != 302:
            print(f"Release not found: {self.url}")
            return False

        # Download the build.
        resp = get(self.url).content
        print("Downloaded the build.")
        # Save the zip file.
        zip_path = Path().home().joinpath(f"{SYSTEM_TO_RELEASE[system()]}.zip")
        zip_path.write_bytes(resp)
        print("Saved the .zip file.")
        # Extract the zip file.
        with zipfile.ZipFile(str(zip_path.resolve()), 'r') as zip_ref:
            zip_ref.extractall(str(BUILD_ROOT_DIR.resolve()))
        print("Extracted the .zip file.")
        # Delete the zip file.
        zip_path.unlink()
        print("Deleted the .zip file.")
        return True


class PyPiVersion:
    """
    Compare the version of the installed tdw Python module to the PyPi version.
    """

    @staticmethod
    def strip_post_release(v: str) -> str:
        """
        If the version number has a post-release suffix (a fourth number), strip it.

        :param v: The version number.

        :return: The version, stripped of the post-release suffix.
        """

        if len(v.split(".")) > 3:
            # Get the post-release suffix and then return a sliced string using its length.
            return v[:-len(re.search(r"(?:.(?!\.))+$", v).group(0))]
        else:
            return v

    @staticmethod
    def _get_pypi_releases() -> List[str]:
        """
        :return: A list of all available PyPi releases.
        """

        # Get an error from  PyPi which will list all available versions.
        p = Popen(["pip3", "install", "tdw=="], stderr=PIPE, shell=True, stdout=PIPE)
        p.wait()
        stdout, stderr = p.communicate()
        # From the list of available versions, get the last one (the most recent).
        versions = re.search(r"\(from versions: (.*)\)", stderr.decode("utf-8")).group(1).split(",")
        return [v.strip() for v in versions]

    @staticmethod
    def get_pypi_version(truncate: bool = False) -> str:
        """
        :param truncate: If true, remove the post-release number (the fourth number) if there is one.

        :return: The newest available tdw release on PyPi.
        """

        # From the list of available versions, get the last one (the most recent).
        v = PyPiVersion._get_pypi_releases()[-1]

        # Strip the post-release suffix.
        if truncate:
            return PyPiVersion.strip_post_release(v)
        else:
            return v

    @staticmethod
    def get_installed_tdw_version(truncate: bool = False) -> str:
        """
        :param truncate: If true, remove the post-release number (the fourth number) if there is one.

        :return: The version of the tdw Python module installed on this machine.
        """

        # Get info on the tdw module.
        p = check_output(["pip3", "show", "tdw"], shell=True).decode("utf-8")
        # Get the version from the output.
        v = re.search(r"Version: (.*)", p, flags=re.MULTILINE).group(1).strip()

        # Strip the post-release suffix.
        if truncate:
            return PyPiVersion.strip_post_release(v)
        else:
            return v

    @staticmethod
    def get_latest_post_release(v: str) -> str:
        """
        :param v: A three-part version string, e.g. 1.6.1

        :return: The most up-to-date version or post-release of the tdw module on PyPi with `v`, e.g. 1.6.1.10
        """

        releases = PyPiVersion._get_pypi_releases()
        releases = sorted([r for r in releases if r.startswith(v)])
        if len(releases) == 0:
            return ""
        return releases[-1]
