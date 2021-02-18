from abc import ABC, abstractmethod
from pathlib import Path
import platform
from typing import List
from subprocess import call, check_output, CalledProcessError
import os
import pkg_resources
import re


class AssetBundleCreatorBase(ABC):
    """
    Base class for creating asset bundles.
    """

    UNITY_VERSION = "2020.2"

    def __init__(self, quiet: bool = False, display: str = ":0"):
        """
        :param quiet: If true, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        """

        # Get the binaries path and verify that AssetBundleCreator will work on this platform.
        system = platform.system()

        self.env = os.environ.copy()

        # libgconf needs to be installed the Editor to work.
        if system == "Linux":
            try:
                check_output(["dpkg", "-l", "libgconf-2-4"])
            except CalledProcessError as e:
                raise Exception(f"{e}\n\nRun: sudo apt install libgconf-2-4")
            # Set the display for Linux.
            self.env["DISPLAY"] = display

        self.quiet = quiet

        self.project_path = self.get_unity_project()
        assert self.project_path.exists(), self.project_path

        self.unity_call = self.get_base_unity_call()

    def get_base_unity_call(self) -> List[str]:
        """
        :return The call to launch Unity Editor silently in batchmode, execute something, and then quit.
        """

        return [str(AssetBundleCreatorBase.get_editor_path().resolve()),
                "-projectpath",
                str(self.project_path.resolve()),
                "-quit",
                "-batchmode"]

    @staticmethod
    def get_editor_path() -> Path:
        system = platform.system()

        # Get the path to the Editor executable.
        if system == "Windows":
            editor_path = Path('C:/Program Files/Unity/Hub/Editor/')

            # Sometimes Unity Hub is installed here instead.
            if not editor_path.exists():
                editor_path = Path('C:/Program Files/Unity Hub/')
        elif system == "Darwin":
            editor_path = Path("/Applications/Unity/Hub/Editor")
        elif system == "Linux":
            editor_path = Path.home().joinpath("Unity/Hub/Editor")
        else:
            raise Exception(f"Platform not supported: {system}")

        assert editor_path.exists(), f"Unity Hub not found: {editor_path}"

        # Get the expected Unity version.
        ds = []
        re_pattern = AssetBundleCreatorBase.UNITY_VERSION + ".(.*)"
        for d in editor_path.iterdir():
            if AssetBundleCreatorBase.UNITY_VERSION not in d.stem:
                continue
            re_search = re.search(re_pattern, str(d.resolve()))
            if re_search is None:
                continue
            ds.append(d)
        ds = sorted(ds, key=lambda version: int(re.search(re_pattern, str(version.resolve())).group(1), 16))
        editor_version = ds[-1]
        editor_path = editor_path.joinpath(editor_version)

        if system == "Windows":
            editor_path = editor_path.joinpath("Editor/Unity.exe")
        elif system == "Darwin":
            editor_path = editor_path.joinpath("Unity.app/Contents/MacOS/Unity")
        elif system == "Linux":
            editor_path = editor_path.joinpath("Editor/Unity")
        else:
            raise Exception(f"Platform not supported: {system}")
        assert editor_path.exists(), f"Unity Editor {editor_version} not found."

        return editor_path

    def get_unity_project(self) -> Path:
        """
        Build the asset_bundle_creator Unity project.

        :return The path to the asset_bundle_creator Unity project.
        """

        unity_project_path = self.get_project_path()

        # If the project already exists, stop.
        if unity_project_path.exists():
            return unity_project_path

        if not self.quiet:
            print(f"Creating: {unity_project_path.resolve()}")

        call([str(AssetBundleCreatorBase.get_editor_path().resolve()),
              "-createProject",
              str(unity_project_path.resolve()),
              "-quit",
              "-batchmode"], env=self.env)
        assert unity_project_path.exists(), unity_project_path.resolve()
        if not self.quiet:
            print(f"Created new Unity project: {str(unity_project_path.resolve())}")

        # Import the package.
        self.import_unity_package(unity_project_path=unity_project_path)

        return unity_project_path

    def import_unity_package(self, unity_project_path: Path) -> None:
        """
        Import the .unitypackage file into the Unity project.

        :param unity_project_path: The path to the Unity project.
        """

        # Add the .unitypackage to the new project.
        package_name = self.get_unity_package()
        filepath = pkg_resources.resource_filename(__name__, package_name)
        assert Path(filepath).exists(), filepath
        # Import the package.
        call([str(AssetBundleCreatorBase.get_editor_path().resolve()),
              "-projectPath",
              str(unity_project_path.resolve()),
              "-importPackage",
              filepath,
              "-quit",
              "-batchmode"], env=self.env)
        if not self.quiet:
            print(f"Imported {package_name} into the new project.")

    @staticmethod
    @abstractmethod
    def get_project_path() -> Path:
        """
        :return: The expected path of the Unity project.
        """

        raise Exception()

    @staticmethod
    @abstractmethod
    def get_unity_package() -> str:
        """
        :return: The name of the .unitypackage file.
        """

        raise Exception()

