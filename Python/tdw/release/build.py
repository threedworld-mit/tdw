from os import getcwd, chdir
from subprocess import call
from requests import get, head
from typing import Tuple
from platform import system
from pathlib import Path
from zipfile import ZipFile
from distutils import dir_util
import tarfile
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
    def get_url(version: str = __version__, check_head: bool = True) -> Tuple[str, bool]:
        """
        :param version: The version of the build. Default = the installed version of TDW.
        :param check_head: If True, check the HTTP headers to make sure that the release exists.

        :return: The URL of the build release matching the version and the OS of this machine, True if the URL exists.
        """

        url = f"https://github.com/threedworld-mit/tdw/releases/download/{version}/" \
              f"{SYSTEM_TO_RELEASE[system()]}"
        if system() == "Windows":
            url += ".zip"
        else:
            url += ".tar.gz"
        # Check if the URL exists.
        if check_head and head(url).status_code != 302:
            print(f"Release not found: {url}")
            release_exists = False
        else:
            release_exists = True
        return url, release_exists

    @staticmethod
    def download(version: str = __version__, v_prefix: bool = True) -> bool:
        """
        Download the release corresponding to this version. Move it to the build path and extract it.

        :param version: The version of the build. Default = the installed version of TDW.
        :param v_prefix: If True, add a `v` to the start of the `version` string.

        :return: True if the build downloaded.
        """

        if v_prefix:
            version = "v" + version

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
        platform = system()
        filename = f"{SYSTEM_TO_RELEASE[platform]}"
        if platform == "Windows":
            filename += ".zip"
        else:
            filename += ".tar.gz"
        zip_path = Path().home().joinpath(filename)
        zip_path.write_bytes(resp)
        print("Saved the file.")

        dst = str(Build.BUILD_ROOT_DIR.resolve())
        # Extract the zip file.
        if platform == "Windows":
            with ZipFile(str(zip_path.resolve()), 'r') as zip_ref:
                zip_ref.extractall(dst)
        else:
            tar = tarfile.open(str(zip_path.resolve()))
            tar.extractall(dst)
            tar.close()
        # Run this to fixed "Damaged App" errors.
        # Source: https://www.google.com/search?client=firefox-b-1-d&q=unity+damaged+app
        if platform == "Darwin":
            cwd = getcwd()
            chdir(str(Build.BUILD_ROOT_DIR.joinpath("TDW").resolve()))
            call(["xattr", "-r", "-d", "com.apple.quarantine", "TDW.app"])
            chdir(cwd)
        print(f"Extracted the file to: {dst}")
        # Delete the zip file.
        zip_path.unlink()
        print("Deleted the download file.")
        return True
