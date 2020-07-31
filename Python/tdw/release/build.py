from requests import get, head
from typing import Tuple
from platform import system
from pathlib import Path
from zipfile import ZipFile
from distutils import dir_util
from subprocess import call
from tdw.version import __version__
from tdw.backend.platforms import SYSTEM_TO_RELEASE, SYSTEM_TO_EXECUTABLE


class Build:
    """
    Various helper functions for TDW builds.
    """

    BUILD_ROOT_DIR = Path.home().joinpath(f"tdw_build")
    BUILD_PATH = BUILD_ROOT_DIR.joinpath(f"TDW/TDW{SYSTEM_TO_EXECUTABLE[system()]}")
    if system() == "Darwin":
        BUILD_PATH = BUILD_PATH.joinpath("Contents/MacOS/TDW")

    @staticmethod
    def get_url(version: str = __version__) -> Tuple[str, bool]:
        """
        :param version: The version of the build. Default = the installed version of TDW.

        :return: The URL of the build release matching the version and the OS of this machine, True if the URL exists.
        """

        url = f"https://github.com/threedworld-mit/tdw/releases/download/v{version}/" \
              f"{SYSTEM_TO_RELEASE[system()]}.zip"
        # Check if the URL exists.
        if head(url).status_code != 302:
            print(f"Release not found: {url}")
            release_exists = False
        else:
            release_exists = True
        return url, release_exists

    @staticmethod
    def chmod() -> None:
        """
        Add execute permissions to the build.
        :return:
        """

        if system() == "Darwin" or system() == "Linux":
            call(["chmod", "+x", str(Build.BUILD_PATH.resolve())])

    @staticmethod
    def download(version: str = __version__) -> bool:
        """
        Download the release corresponding to this version. Move it to the build path and extract it.

        :param version: The version of the build. Default = the installed version of TDW.

        :return: True if the build downloaded.
        """

        url, url_exists = Build.get_url(version)
        if not url_exists:
            return False

        if Build.BUILD_ROOT_DIR.exists():
            dir_util.remove_tree(str(Build.BUILD_ROOT_DIR.resolve()))
            print("Deleted old release.")

        # Download the build.
        resp = get(url).content
        print("Downloaded the build.")
        # Save the zip file.
        zip_path = Path().home().joinpath(f"{SYSTEM_TO_RELEASE[system()]}.zip")
        zip_path.write_bytes(resp)
        print("Saved the .zip file.")
        # Extract the zip file.
        with ZipFile(str(zip_path.resolve()), 'r') as zip_ref:
            zip_ref.extractall(str(Build.BUILD_ROOT_DIR.resolve()))
        print(f"Extracted the .zip file to: {Build.BUILD_ROOT_DIR.resolve()}")
        # Delete the zip file.
        zip_path.unlink()
        print("Deleted the .zip file.")

        # Add execute permissions.
        Build.chmod()
        return True
