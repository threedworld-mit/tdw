from os import chdir, getcwd
from json import loads
from platform import system
from pathlib import Path
from zipfile import ZipFile
import tarfile
from subprocess import call
from packaging.version import Version, parse
from shutil import rmtree
from requests import get, head
from tdw import __version__
from tdw.backend.platforms import SYSTEM_TO_RELEASE
from tdw.backend.paths import BUILD_PATH, BUILD_ROOT_DIR


class Update:
    """
    Check for updates on PyPi. If there are any, let the user know.

    Check if the build version is behind the local Python version. If so, download a new build.
    """

    @staticmethod
    def get_pypi_version() -> str:
        """
        :return: The latest version of TDW on PyPi.
        """

        # Get the newest version on PyPi.
        resp = get("https://pypi.org/pypi/tdw/json")
        data = loads(resp.content)
        versions = list(data["releases"].keys())
        versions.sort(key=lambda s: list(map(int, s.split('.'))))
        return versions[-1]

    @staticmethod
    def check_for_update(download_build: bool) -> bool:
        """
        Get the latest version of TDW on PyPi and compare it to the locally installed version.
        Tell the user to upgrade if needed.

        Optionally, compare the version of the build to the locally installed Python version.
        If there is a mismatch, download the build.

        :param download_build: If True, check the version of the build and download a new one if needed.

        :return: True if it is possible to launch the build.
        """

        pypi_version: Version = parse(Update.get_pypi_version())

        # Get the local version.
        local_version: Version = parse(__version__)

        if local_version < pypi_version:
            print(f"You are using TDW {local_version} but version {pypi_version} is available.\n"
                  f"Consider upgrading:\npip3 install tdw -U")
        else:
            print("Your installed tdw Python module is up to date with PyPi.")

        if not download_build:
            return False

        # Check if the build needs to be updated.
        need_to_download = False
        local_py_release_version: Version = parse(".".join([str(q) for q in local_version.release[:-1]]))
        if not BUILD_PATH.exists():
            print(f"Couldn't find build at {BUILD_PATH}\nDownloading now...")
            need_to_download = True
            build_version: Version = local_py_release_version
        else:
            # Check versions.
            build_version_path = BUILD_ROOT_DIR.joinpath("TDW/version.txt")
            if build_version_path.exists():
                build_version = parse(build_version_path.read_text().strip())
                if build_version < local_py_release_version:
                    print(f"Python version is {local_py_release_version} but the build version is {build_version}.\n"
                          f"Downloading version {local_py_release_version} of the build now...")
                    build_version = local_py_release_version
                    need_to_download = True
            else:
                "Failed to find build version!"
                need_to_download = True
                build_version = local_py_release_version

        if not need_to_download:
            return True

        # Get the download URL.
        download_version = "v" + str(build_version)
        url = f"https://github.com/threedworld-mit/tdw/releases/download/{download_version}/" \
              f"{SYSTEM_TO_RELEASE[system()]}"
        if system() == "Windows":
            url += ".zip"
        else:
            url += ".tar.gz"
        # Check if the URL exists.
        if head(url).status_code != 302:
            print(f"Release not found: {url}")
            return False

        if BUILD_ROOT_DIR.exists():
            rmtree(str(BUILD_ROOT_DIR.resolve()))
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

        dst = str(BUILD_ROOT_DIR.resolve())
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
            chdir(str(BUILD_ROOT_DIR.joinpath("TDW").resolve()))
            call(["xattr", "-r", "-d", "com.apple.quarantine", "TDW.app"])
            chdir(cwd)
        print(f"Extracted the file to: {dst}")
        # Delete the zip file.
        zip_path.unlink()
        print("Deleted the download file.")
        return True

