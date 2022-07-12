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

    @final
    def prefab_to_asset_bundles(self, name: str, output_directory: Union[str, Path]) -> None:
        """
        Build asset bundles from a .prefab file. This is useful when you want to edit the .prefab file by hand, e.g.:

        1. `self.source_file_to_prefab()`
        2. Edit .prefab file
        3. `self.prefab_to_asset_bundles()`

        Example source:

        ```
        ~/asset_bundle_creator/
        ....Assets/
        ........prefabs/
        ............name.prefab
        ........source_files/
        ............name/
        ................name.obj
        ................Materials/
        ```

        Example output:

        ```
        output_directory/
        ....Darwin/
        ........name
        ....Linux/
        ........name
        ....Windows/
        ........name
        ```

        :param name: The name of the model (the name of the .prefab file, minus the extension).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        """

        if isinstance(output_directory, Path):
            dst = str(output_directory.resolve())
        else:
            dst = output_directory
        self.call_unity(method="PrefabToAssetBundles", args=[f'-name="{name}"',
                                                             "-source=temp",
                                                             f'-output_directory="{dst}"'])
        self._print_log(output_directory=output_directory)

    @final
    def cleanup(self) -> None:
        """
        Delete any intermediary files in the `asset_bundle_creator` Unity Editor project such as .prefab files.
        """

        self.call_unity(method="Cleanup", args=["-name=temp",
                                                "-source=temp",
                                                "-output_directory=temp",
                                                "-cleanup"])

    @abstractmethod
    def get_creator_class_name(self) -> str:
        """
        :return: The name of the Unity C# class, e.g. `ModelCreatorLauncher`.
        """

        raise Exception()

    @final
    def _print_log(self, output_directory: Union[str, Path]) -> None:
        """
        Print the log file generated by the `asset_bundle_creator` Unity Editor project.

        :param output_directory: The directory where we expect the log to be.
        """

        if self._quiet:
            return
        if isinstance(output_directory, Path):
            f = output_directory.joinpath("log.txt")
        else:
            f = Path(output_directory).joinpath("log.txt")
        if not f.exists():
            print(f"Log file doesn't exist: {f}")
            return
        print(f.read_text(encoding="utf-8"))

    @staticmethod
    def _add_library_path(args: List[str], library_path: Union[str, Path] = None) -> List[str]:
        """
        Add a `-library_path=path` argument to a list of arguments.

        :param args: The list of arguments.
        :param library_path: The library path. Can be None.

        :return: The modified list of arguments.
        """

        if library_path is not None:
            if isinstance(library_path, Path):
                args.append(f'-library_path="{str(library_path.resolve())}"')
            elif isinstance(library_path, str):
                args.append(f'-library_path="{library_path}"')
            else:
                raise Exception(library_path)
        return args

    @staticmethod
    def _get_source_destination_args(name: str, source: Union[str, Path], destination: Union[str, Path]) -> List[str]:
        """
        Parse a source path and a destination path into Unity command line arguments.

        :param name: The model name.
        :param source: The source path.
        :param destination: The destination path.

        :return: A list of arguments.
        """

        if isinstance(source, Path):
            src = str(source.resolve())
        else:
            src = source
        if isinstance(destination, Path):
            dst = str(destination.resolve())
        else:
            dst = destination
        return [f'-name="{name}"',
                f'-source={src}"',
                f'-output_directory="{dst}"']
