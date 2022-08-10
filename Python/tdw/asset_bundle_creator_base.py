from abc import ABC, abstractmethod
from pathlib import Path
import platform
from typing import List, Union
from subprocess import call, check_output, CalledProcessError, Popen
import os
import re
from time import sleep
from overrides import final
from tdw.backend.platforms import SYSTEM_TO_UNITY


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
        """:field
        If True, don't print any messages to console.
        """
        self.quiet: bool = quiet
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
    def call_unity(self, method: str, args: List[str], log_path: Union[str, Path], class_name: str = None) -> None:
        """
        Execute a call to Unity Editor. If `self.quiet == False` this will continuously print the log file.

        :param method: The name of the method.
        :param args: Arguments to send to Unity Editor in addition to those send via `self.get_base_unity_call()` and `-executeMethod`.
        :param log_path:  The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
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
        if self.quiet:
            call(unity_call, env=self._env)
        else:
            self.run_process_and_print_log(process=Popen(unity_call, env=self._env, shell=True),
                                           log_path=log_path)

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
        ....log.txt
        ```

        :param name: The name of the model (the name of the .prefab file, minus the extension).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        """

        self.call_unity(method="PrefabToAssetBundles",
                        args=[f'-name="{name}"',
                              "-source=temp",
                              f'-output_directory="{AssetBundleCreatorBase._get_string_path(output_directory)}"'],
                        log_path=AssetBundleCreatorBase._get_path(output_directory).joinpath("log.txt"))

    @final
    def cleanup(self) -> None:
        """
        Delete any intermediary files in the `asset_bundle_creator` Unity Editor project such as .prefab files.
        """

        self.call_unity(method="Cleanup",
                        args=["-name=temp",
                              "-source=temp",
                              "-output_directory=temp",
                              "-cleanup"],
                        log_path="")

    @abstractmethod
    def get_creator_class_name(self) -> str:
        """
        :return: The name of the Unity C# class, e.g. `ModelCreatorLauncher`.
        """

        raise Exception()

    @staticmethod
    def asset_bundles_exist(name: str, output_directory: Union[str, Path]) -> bool:
        """
        :param name: The name of the asset bundle (the filename).
        :param output_directory: The *root* output directory of *all* of the platform-specific asset bundles as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If an asset bundle is located in `/home/user/output_directory/Windows/asset_bundle`, set this to `"/home/user/output_directory"`.

        :return: True if asset bundles for all three platforms exist in `output_directory`.
        """

        d = AssetBundleCreatorBase._get_path(output_directory)
        for p in SYSTEM_TO_UNITY:
            if not d.joinpath(p).joinpath(name).exists():
                return False
        return True

    @staticmethod
    def run_process_and_print_log(process: Popen, log_path: Union[str, Path], sleep_time: float = 1) -> None:
        """
        Poll a process to check if it is completed. If not, try to read a log file. Print the new text of the log file.

        :param process: The process.
        :param log_path: The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param sleep_time: The time in seconds to wait between process polling.
        """

        path = AssetBundleCreatorBase._get_path(log_path)
        previous_log_text = ""
        while process.poll() is None:
            # Update the log text.
            previous_log_text = AssetBundleCreatorBase._read_log_text(previous_log_text=previous_log_text, log_path=path)
            sleep(sleep_time)
        # Finish reading the log.
        AssetBundleCreatorBase._read_log_text(previous_log_text=previous_log_text, log_path=path)

    @staticmethod
    def _read_log_text(previous_log_text: str, log_path: Path) -> str:
        """
        Read the log and show only the text that we haven't seen yet.

        :param previous_log_text: The text that we've seen so far.
        :param log_path: The path to the log file.

        :return: The updated text that we've seen so far.
        """

        # Wait until the log exists.
        if not log_path.exists():
            return previous_log_text
        try:
            log_text = log_path.read_text(encoding="utf-8")
            # Only show the new text.
            show_text = log_text.replace(previous_log_text, "")
            if len(show_text) > 0:
                print(show_text)
                # Hide the text for next time.
                return log_text[:]
            else:
                return previous_log_text
        # We might have to wait because Unity is writing to the file.
        except PermissionError:
            return previous_log_text

    @staticmethod
    def _add_library_args(args: List[str], library_path: Union[str, Path] = None, library_description: str = None) -> List[str]:
        """
        Add a `-library_path=path` argument to a list of arguments.

        :param args: The list of arguments.
        :param library_path: The library path. Can be None.
        :param library_description: A description of the library. Can be None.

        :return: The modified list of arguments.
        """

        if library_path is not None:
            args.append(f'-library_path="{AssetBundleCreatorBase._get_string_path(library_path)}"')
        if library_description is not None:
            args.append(f'-library_description="{library_description}"')
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

        return [f'-name="{name}"',
                f'-source="{AssetBundleCreatorBase._get_string_path(source)}"',
                f'-output_directory="{AssetBundleCreatorBase._get_string_path(destination)}"']

    @staticmethod
    def _get_path(path: Union[str, Path]) -> Path:
        """
        :param path: A path as either a string or a `Path`.

        :return: The path as a `Path`.
        """

        if isinstance(path, str):
            return Path(path)
        elif isinstance(path, Path):
            return path
        else:
            raise Exception(path)

    @staticmethod
    def _get_string_path(path: Union[str, Path]) -> str:
        """
        :param path: A path as either a string or a `Path`.

        :return: The path as a string.
        """

        if isinstance(path, str):
            p = path
        elif isinstance(path, Path):
            p = str(path.resolve())
        else:
            raise Exception(path)
        return p.replace("\\", "/")
