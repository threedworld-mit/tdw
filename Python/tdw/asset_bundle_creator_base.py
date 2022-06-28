from abc import ABC, abstractmethod
from pathlib import Path
import platform
from typing import List, Union
from subprocess import call, check_output, CalledProcessError
import os
import re
from overrides import final


class AssetBundleCreatorBase(ABC):
    """
    Base class for creating asset bundles.
    """

    """:class_var
    Use this version of Unity Editor to launch the asset bundle creator.
    """
    UNITY_VERSION: str = "2020.3"
    """:class_var
    The path to the `asset_bundle_creator` Unity project.
    """
    PROJECT_PATH: Path = Path.home().joinpath("asset_bundle_creator")

    def __init__(self, quiet: bool = False, display: str = ":0", unity_editor_path: Union[Path, str] = None):
        """
        :param quiet: If True, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        :param unity_editor_path: The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically.
        """

        # Get the binaries path and verify that AssetBundleCreator will work on this platform.
        system = platform.system()
        # Copy environment variables.
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
            self._unity_editor_path: Path = editor_path
        else:
            if isinstance(unity_editor_path, Path):
                self._unity_editor_path = unity_editor_path
            elif isinstance(unity_editor_path, str):
                self._unity_editor_path = Path(unity_editor_path)
            else:
                raise Exception(f"Invalid Unity editor path: {self._unity_editor_path}")
            assert self._unity_editor_path.exists(), "Unity Editor not found: " + str(self._unity_editor_path.resolve())

    @final
    def get_base_unity_call(self) -> List[str]:
        """
        :return The call to launch Unity Editor silently in batchmode, execute something, and then quit.
        """

        return [str(self._unity_editor_path.resolve()),
                "-projectpath",
                str(AssetBundleCreatorBase.PROJECT_PATH.resolve()),
                "-quit",
                "-batchmode"]

    @final
    def call_unity(self, method: str, args: List[str], class_name: str = None) -> None:
        """
        Execute a call to Unity Editor.

        :param method: The name of the method.
        :param args: Arguments to send to Unity Editor in addition to those send via `self.get_base_unity_call()` and `-executeMethod`.
        :param class_name: The name of the Unity C# class. If None, a default class name will be used. See: `self.get_creator_class_name()`.
        """

        # Clone the repo.
        if not AssetBundleCreatorBase.PROJECT_PATH.exists():
            cwd = os.getcwd()
            os.chdir(str(Path.home().resolve()))
            call(["git", "clone", "https://github.com/alters-mit/asset_bundle_creator.git"])
            os.chdir(cwd)
        # Get the base Unity call.
        unity_call = self.get_base_unity_call()
        # Get the class name.
        if class_name is None:
            class_name = self.get_creator_class_name()
        # Add arguments to execute a C# method.
        unity_call.extend(["-executeMethod", f"{class_name}.{method}"])
        # Add additional arguments.
        unity_call.extend(args)
        # Call Unity Editor.
        call(unity_call, env=self._env)

    @abstractmethod
    def get_creator_class_name(self) -> str:
        """
        :return: The name of the Unity C# class, e.g. `ModelCreatorLauncher`.
        """

        raise Exception()
