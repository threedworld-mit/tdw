from abc import ABC, abstractmethod
from pathlib import Path
import platform
from typing import List, Union
from subprocess import check_output, CalledProcessError
import os
import re


class AssetBundleCreatorBase(ABC):
    """
    Base class for creating asset bundles.
    """

    """:class_var
    Use this version of Unity Editor to launch the asset bundle creator.
    """
    UNITY_VERSION: str = "2020.3"

    def __init__(self, quiet: bool = False, display: str = ":0", unity_editor_path: Union[Path, str] = None):
        """
        :param quiet: If True, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        :param unity_editor_path: The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically.
        """

        # Get the binaries path and verify that AssetBundleCreator will work on this platform.
        system = platform.system()

        self._env = os.environ.copy()

        # libgconf needs to be installed the Editor to work.
        if system == "Linux":
            try:
                check_output(["dpkg", "-l", "libgconf-2-4"])
            except CalledProcessError as e:
                raise Exception(f"{e}\n\nRun: sudo apt install libgconf-2-4")
            # Set the display for Linux.
            self._env["DISPLAY"] = display
        self._quiet: bool = quiet
        # Get the Unity path.
        if unity_editor_path is None:
            self._unity_editor_path: Path = AssetBundleCreatorBase._get_editor_path()
        else:
            if isinstance(unity_editor_path, Path):
                self._unity_editor_path = unity_editor_path
            elif isinstance(unity_editor_path, str):
                self._unity_editor_path = Path(unity_editor_path)
            else:
                raise Exception(f"Invalid Unity editor path: {self._unity_editor_path}")
            assert self._unity_editor_path.exists(), "Unity Editor not found: " + str(self._unity_editor_path.resolve())
        self._project_path: Path = self.get_unity_project()
        assert self._project_path.exists(), self._project_path
        self._unity_call: List[str] = self.get_base_unity_call()

    def get_base_unity_call(self) -> List[str]:
        """
        :return The call to launch Unity Editor silently in batchmode, execute something, and then quit.
        """

        return [str(self._unity_editor_path.resolve()),
                "-projectpath",
                str(self._project_path.resolve()),
                "-quit",
                "-batchmode"]

    @staticmethod
    def _get_editor_path() -> Path:
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

    @abstractmethod
    def get_unity_project(self) -> Path:
        """
        Build the asset_bundle_creator Unity project.

        :return The path to the asset_bundle_creator Unity project.
        """

        raise Exception()

    @staticmethod
    @abstractmethod
    def get_project_path() -> Path:
        """
        :return: The expected path of the Unity project.
        """

        raise Exception()
