import re
from pathlib import Path
import platform
from typing import List, Tuple, Union
from subprocess import call, check_output, CalledProcessError
import os
import shutil
from tdw.librarian import ModelRecord
import json
from tdw.asset_bundle_creator_base import AssetBundleCreatorBase
from tdw.add_ons.model_verifier.model_verifier import ModelVerifier
from tdw.controller import Controller


class AssetBundleCreator:
    """
    Given a .fbx file or a .obj file, and (optionally) Materials and/or Textures folder adjacent to that file,
    create asset bundles for Windows, OS X, and Linux.

    Usage:

    ```python
    from tdw.asset_bundle_creator import AssetBundleCreator

    a = AssetBundleCreator()

    # Typically this is the only function you'll want to call.
    asset_bundle_paths, record_path = a.create_asset_bundle("cube.fbx", cleanup=True)
    ```

    For more information, see: `Documentation/misc_frontend/add_local_object.md`.
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
        self._unity_call: List[str] = self.get_base_unity_call()

    @staticmethod
    def get_editor_path() -> Path:
        """
        :return: The path to Unity Editor as a [`Path`](https://docs.python.org/3/library/pathlib.html).
        """

        system = platform.system()
        # Get the path to the Editor executable.
        if system == "Windows":
            editor_path = Path('C:/Program Files/Unity/Hub/Editor/')
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

    def get_base_unity_call(self) -> List[str]:
        """
        :return The call to launch Unity Editor silently in batchmode, execute something, and then quit.
        """

        return [str(self._unity_editor_path.resolve()),
                "-projectpath",
                str(AssetBundleCreator.PROJECT_PATH.resolve()),
                "-quit",
                "-batchmode"]

    def do_unity_call(self, method: str, args: List[str]) -> None:
        """
        Execute a call to Unity Editor.

        :param method: The name of the method.
        :param args: Arguments to send to Unity Editor in addition to those send via `self.get_base_unity_call()`.
        """

        # Clone the repo.
        if not AssetBundleCreator.PROJECT_PATH.exists():
            cwd = os.getcwd()
            os.chdir(str(Path.home().resolve()))
            call(["git", "clone", "https://github.com/alters-mit/asset_bundle_creator.git"])
            os.chdir(cwd)
        unity_call = self.get_base_unity_call()
        unity_call.extend(["-executeMethod", method])
        unity_call.extend(args)
        call(unity_call, env=self._env)

    def source_directory_to_asset_bundles(self, source_directory: Union[str, Path], output_directory: Union[str, Path],
                                          library_description: str = None, vhacd_resolution: int = None,
                                          internal_materials: bool = False) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_directory, destination=output_directory)
        if library_description is not None:
            args.append(f"-library_description={library_description}")
        if vhacd_resolution is not None:
            args.append(f"-vhacd_resolution={vhacd_resolution}")
        if internal_materials:
            args.append("-internal_materials")
        # Execute the call.
        self.do_unity_call(method="ModelCreatorLauncher.ModelSourceDirectoryToAssetBundles", args=args)

    def source_file_to_prefab(self, source_file: Union[str, Path], output_directory: Union[str, Path],
                              vhacd_resolution: int = None, internal_materials: bool = False) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        if vhacd_resolution is not None:
            args.append(f"-vhacd_resolution={vhacd_resolution}")
        if internal_materials:
            args.append("-internal_materials")
        # Execute the call.
        self.do_unity_call(method="ModelCreatorLauncher.ModelSourceFileToPrefab", args=args)

    def prefab_to_asset_bundles(self, source_file: Union[str, Path]) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination="")
        # Execute the call.
        self.do_unity_call(method="ModelCreatorLauncher.ModelPrefabToAssetBundles", args=args)

    def move_asset_bundles(self, source_file: Union[str, Path], output_directory: Union[str, Path]) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        # Execute the call.
        self.do_unity_call(method="ModelCreatorLauncher.MoveModelAssetBundles", args=args)

    def create_record(self, source_file: Union[str, Path], output_directory: Union[str, Path],
                      wnid: str = None, wcategory: str = None, scale_factor: float = None,
                      library_path: Union[str, Path] = None) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        for value, flag in zip([wnid, wcategory, scale_factor], ["wnid", "wcategory", "scale_factor"]):
            if value is not None:
                args.append(f"-{flag}={value}")
        if library_path is not None:
            if isinstance(library_path, Path):
                args.append(f"-library_path={str(library_path.resolve())}")
            elif isinstance(library_path, str):
                args.append(f"-library_path={library_path}")
            else:
                raise Exception(library_path)
        # Execute the call.
        self.do_unity_call(method="ModelCreatorLauncher.MoveModelAssetBundles", args=args)

    def cleanup(self, source_file: Union[str, Path], output_directory: Union[str, Path]) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        args.append("-cleanup")
        # Execute the call.
        self.do_unity_call(method="ModelCreatorLauncher.ModelCreatorCleanup", args=args)

    def source_file_to_asset_bundles(self, source_file: Union[str, Path], output_directory: Union[str, Path],
                                     vhacd_resolution: int = None, internal_materials: bool = False,
                                     wnid: str = None, wcategory: str = None, scale_factor: float = None,
                                     library_path: Union[str, Path] = None, cleanup: bool = True) -> None:
        self.source_file_to_prefab(source_file=source_file, output_directory=output_directory,
                                   vhacd_resolution=vhacd_resolution, internal_materials=internal_materials)
        self.prefab_to_asset_bundles(source_file=source_file)
        self.move_asset_bundles(source_file=source_file, output_directory=output_directory)
        self.create_record(source_file=source_file, output_directory=output_directory, wnid=wnid, wcategory=wcategory,
                           scale_factor=scale_factor, library_path=library_path)
        if cleanup:
            self.cleanup(source_file=source_file, output_directory=output_directory)

    @staticmethod
    def write_physics_quality(record_path: Path, asset_bundle_path: Path) -> None:
        """
        Append the physics quality data to the temporary record file.
        This is an optional record field that records the percentage of the model encapsualted by colliders.

        :param record_path: The path to the temporary record file.
        :param asset_bundle_path: The URL to the local asset bundle.
        """

        c = Controller()
        v = ModelVerifier()
        r: ModelRecord = ModelRecord(json.loads(Path(record_path).read_text(encoding="utf-8")))
        original_url = r.urls[platform.system()]
        r.urls[platform.system()] = f"file:///{str(asset_bundle_path)}"
        v.set_tests(name=r.name, source=r, model_report=False, missing_materials=False, physics_quality=True)
        c.add_ons.append(v)
        c.communicate([])
        while not v.done:
            c.communicate([])
        c.communicate({"$type": "terminate"})
        c.socket.close()
        # Write the physics quality.
        r.physics_quality = float(v.reports[0])
        r.urls[platform.system()] = original_url
        record_path.write_text(json.dumps(r.__dict__), encoding="utf-8")

    def validate(self, record_path: Path, asset_bundle_path: Path) -> Tuple[bool, str]:
        """
        Validate the asset bundle.

        :param record_path: The path to the temporary record file.
        :param asset_bundle_path: The URL to the local asset bundle.

        :return True if there aren't problems, and a string output report.
        """

        if not self._quiet:
            print("Validating asset bundle...")

        c = Controller()
        v = ModelVerifier()
        r: ModelRecord = ModelRecord(json.loads(Path(record_path).read_text(encoding="utf-8")))
        r.urls[platform.system()] = f"file:///{str(asset_bundle_path)}"
        v.set_tests(name=r.name, source=r, model_report=True, missing_materials=True, physics_quality=False)
        c.add_ons.append(v)
        c.communicate([])
        while not v.done:
            c.communicate([])
        c.communicate({"$type": "terminate"})
        c.socket.close()
        if len(v.reports) != 0:
            output = "There are problems with the asset bundle!"
            for problem in v.reports:
                output += "\n\t" + problem
            return False, output
        if not self._quiet:
            print("OK!")
        return True, ""

    @staticmethod
    def _get_src_dst(source: Union[str, Path], destination: Union[str, Path]) -> List[str]:
        if isinstance(source, Path):
            src = str(source.resolve())
        else:
            src = source
        if isinstance(destination, Path):
            dst = str(destination.resolve())
        else:
            dst = destination
        return [f"-source_directory={src}",
                f"-output_directory={dst}"]
