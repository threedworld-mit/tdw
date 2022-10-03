from abc import ABC, abstractmethod
from pathlib import Path
import platform
from typing import List, Union
from subprocess import call, check_output, CalledProcessError, Popen
import os
import re
from time import sleep
from packaging import version
from overrides import final
from requests import get
from tdw.tdw_utils import TDWUtils
from tdw.backend.platforms import SYSTEM_TO_S3


class AssetBundleCreator(ABC):
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
    _BUNDLE_VERSION_REGEX: str = "bundleVersion: (.*)"
    _VERSION_CHECKED: bool = False

    def __init__(self, quiet: bool = False, display: str = ":0", unity_editor_path: Union[Path, str] = None,
                 check_version: bool = True):
        """
        :param quiet: If True, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        :param unity_editor_path: The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically.
        :param check_version: If True, check if there is an update to the Unity Editor project.
        """

        if check_version and not AssetBundleCreator._VERSION_CHECKED and AssetBundleCreator.PROJECT_PATH.exists():
            # Get the local version from ProjectSettings.asset
            local_version = re.search(AssetBundleCreator._BUNDLE_VERSION_REGEX,
                                      AssetBundleCreator.PROJECT_PATH.joinpath(
                                          "ProjectSettings/ProjectSettings.asset").resolve().read_text(),
                                      flags=re.MULTILINE).group(1)
            # Check if the old <= 1.4.1 asset_bundle_creator exists. If so, end here and tell the user to upgrade.
            local_version_parsed = version.parse(local_version)
            if local_version_parsed.major <= 1:
                print("You have an obsolete version of the asset_bundle_creator Unity project. To upgrade:\n"
                      f"1. Delete this directory: {str(AssetBundleCreator.PROJECT_PATH.resolve())}\n"
                      f"2. Run this script again. The updated asset_bundle_creator will automatically be downloaded.")
                # End here because nothing will work with the pre-v2 project.
                exit()
            # Get the remote version from ProjectSettings.assets
            resp = get("https://raw.githubusercontent.com/alters-mit/asset_bundle_creator/main/ProjectSettings/ProjectSettings.asset")
            if resp.status_code == 200:
                remote_version = re.search(AssetBundleCreator._BUNDLE_VERSION_REGEX,
                                           resp.text,
                                           flags=re.MULTILINE).group(1)
                remote_version_parsed = version.parse(remote_version)
                # Print a warning if an update is available.
                if remote_version_parsed < local_version_parsed:
                    print(f'You are using version {local_version} but version {remote_version} is available. To update:\n' +
                          f'cd "{str(AssetBundleCreator.PROJECT_PATH.resolve())}"'
                          f'\ngit pull')
                else:
                    print(f"Your version of the Asset Bundle Creator Unity project is up to date: {local_version}")
            else:
                print("Failed to check version for the Asset Bundle Creator Unity project. Check your Internet connection.")
            # Don't check the version multiple times during runtime.
            AssetBundleCreator._VERSION_CHECKED = True
        # Get the binaries path and verify that AssetBundleCreator will work on this platform.
        system = platform.system()
        # Copy environment variables.
        self._env = os.environ.copy()
        # Some packages need to be installed for the creator to work.
        if system == "Linux":
            try:
                check_output(["dpkg", "-l", "libgconf-2-4"])
            except CalledProcessError as e:
                raise Exception(f"{e}\n\nRun: sudo apt install libgconf-2-4")
            for pkg in ["gcc-9", "libstdc++6"]:
                try:
                    check_output(["dpkg", "-l", pkg])
                except CalledProcessError as e:
                    raise Exception(f"{e}\n\nRun:\n"
                                    f"sudo add-apt-repository ppa:ubuntu-toolchain-r/test\n"
                                    f"sudo apt install {pkg}")
            # Set the display for Linux.
            self._env["DISPLAY"] = display
        """:field
        If True, don't print any messages to console.
        """
        self.quiet: bool = quiet
        # Get the Unity path.
        if unity_editor_path is None:
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
            re_pattern = AssetBundleCreator.UNITY_VERSION + ".(.*)"
            for d in editor_path.iterdir():
                if AssetBundleCreator.UNITY_VERSION not in d.stem:
                    continue
                re_search = re.search(re_pattern, str(d.resolve()))
                if re_search is None:
                    continue
                ds.append(d)
            # Try to find Unity Editor.
            ds = sorted(ds, key=lambda v: int(re.search(re_pattern, str(v.resolve())).group(1), 16))
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
            self._unity_editor_path = TDWUtils.get_path(unity_editor_path)
            assert self._unity_editor_path.exists(), "Unity Editor not found: " + str(self._unity_editor_path.resolve())

    @final
    def get_base_unity_call(self) -> List[str]:
        """
        :return The call to launch Unity Editor silently in batchmode, execute something, and then quit.
        """

        return [str(self._unity_editor_path.resolve()),
                "-projectpath",
                str(AssetBundleCreator.PROJECT_PATH.resolve()),
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

        s = platform.system()
        # Clone the repo.
        if not AssetBundleCreator.PROJECT_PATH.exists():
            cwd = os.getcwd()
            os.chdir(str(Path.home().resolve()))
            call(["git", "clone", "https://github.com/alters-mit/asset_bundle_creator.git"])
            os.chdir(cwd)
            # Run chmod +x for all binaries.
            if s == "Linux" or s == "Darwin":
                executables_directory = AssetBundleCreator.PROJECT_PATH.joinpath(f"executables/{s}")
                for executable_path in ["vhacd/testVHACD", "assimp/assimp"]:
                    call(["chmod", "+x", str(executables_directory.joinpath(executable_path).resolve())])
        # Get the base Unity call.
        unity_call = self.get_base_unity_call()
        # Get the class name.
        if class_name is None:
            class_name = self.get_creator_class_name()
        # Add arguments to execute a C# method.
        unity_call.extend(["-executeMethod", f"{class_name}.{method}"])
        # Add additional arguments.
        unity_call.extend(args)
        # Run everything in the shell if it's Windows, otherwise don't.
        shell = s == "Windows"
        # If we're in quiet mode, call and wait for the process to end.
        if self.quiet:
            call(unity_call, env=self._env, shell=shell)
        # This will run the process asynchronously and check the log and the process until it's done.
        else:
            self._run_process_and_print_log(process=Popen(unity_call, env=self._env, shell=shell), log_path=log_path)

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
                              f'-output_directory="{TDWUtils.get_string_path(output_directory)}"'],
                        log_path=TDWUtils.get_path(output_directory).joinpath("log.txt"))

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

    @staticmethod
    def asset_bundles_exist(name: str, directory: Union[str, Path]) -> bool:
        """
        Check whether asset bundles exist for all platforms in the source directory.

        Expected directory structure:

        ```
        directory/
        ....Darwin/
        ........name
        ....Linux/
        ........name
        ....Windows/
        ........name
        ```

        ...where `name` is an asset bundle file.

        :param name: The name of the asset bundle.
        :param directory: The source directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).

        :return: True if asset bundles exist for all platforms in the source directory.
        """

        d = TDWUtils.get_path(directory)
        for s in SYSTEM_TO_S3:
            path = d.joinpath(s).joinpath(name)
            if not path.exists():
                return False
        return True

    @abstractmethod
    def get_creator_class_name(self) -> str:
        """
        :return: The name of the Unity C# class, e.g. `ModelCreator`.
        """

        raise Exception()

    @staticmethod
    def _run_process_and_print_log(process: Popen, log_path: Union[str, Path], sleep_time: float = 1) -> None:
        """
        Poll a process to check if it is completed. If not, try to read a log file. Print the new text of the log file.

        :param process: The process.
        :param log_path: The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param sleep_time: The time in seconds to wait between process polling.
        """

        # Get the path to the log file.
        path = TDWUtils.get_path(log_path)
        # Don't print this text.
        previous_log_text = ""
        # Wait for the process to end.
        while process.poll() is None:
            # Update the log text.
            previous_log_text = AssetBundleCreator._read_log_text(previous_log_text=previous_log_text, log_path=path)
            sleep(sleep_time)
        # Finish reading the log.
        AssetBundleCreator._read_log_text(previous_log_text=previous_log_text, log_path=path)

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
            args.append(f'-library_path="{TDWUtils.get_string_path(library_path)}"')
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
                f'-source="{TDWUtils.get_string_path(source)}"',
                f'-output_directory="{TDWUtils.get_string_path(destination)}"']

    @staticmethod
    def _get_log_path(output_directory: Union[str, Path]) -> Path:
        """
        :param output_directory: The output directory.

        :return: The expected path to the log file: `output_directory/log.txt`.
        """

        return TDWUtils.get_path(output_directory).joinpath("log.txt")
