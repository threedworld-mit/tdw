from pathlib import Path
import platform
from typing import List, Dict, Optional, Tuple, Union
from subprocess import call
import os
import shutil
from tdw.librarian import ModelRecord
import json
import pkg_resources
import distutils.dir_util
import distutils.file_util
from tdw.backend.platforms import S3_TO_UNITY, SYSTEM_TO_UNITY, UNITY_TO_SYSTEM
from tdw.asset_bundle_creator_base import AssetBundleCreatorBase
from tdw.add_ons.model_verifier.model_verifier import ModelVerifier
from tdw.controller import Controller


class AssetBundleCreator(AssetBundleCreatorBase):
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

    def __init__(self, quiet: bool = False, display: str = ":0", unity_editor_path: Union[Path, str] = None):
        """
        :param quiet: If true, don't print any messages to console.
        :param display: The display to launch Unity Editor on. Ignored if this isn't Linux.
        :param unity_editor_path: The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically.
        """

        super().__init__(quiet=quiet, display=display, unity_editor_path=unity_editor_path)

        system = platform.system()
        self._binaries: Dict[str, str] = dict()
        binary_path = f"binaries/{system}"

        # Cache the binaries.
        self._binaries["assimp"] = f"{binary_path}/assimp/assimp"
        self._binaries["meshconv"] = f"{binary_path}/meshconv/meshconv"
        self._binaries["vhacd"] = f"{binary_path}/vhacd/testVHACD"

        for binary in self._binaries:
            # Add the .exe suffix for Windows.
            if system == "Windows":
                self._binaries[binary] += ".exe"
            # Run chmod +x on everything.
            else:
                call(["chmod", "+x", pkg_resources.resource_filename(__name__, self._binaries[binary])])

    def create_asset_bundle(self, model_path: Union[Path, str], cleanup: bool, wnid: int = -1, wcategory: str = "", scale: float = 1) -> (List[Path], Path):
        """
        Create an asset bundle for each operating system. Typically, this is the only function you'll want to use.
        This function calls in sequence: `fbx_to_obj()`, `obj_to_wrl()`, `wrl_to_obj()`, `move_files_to_unity_project()`, `create_prefab()`, `prefab_to_asset_bundle()`, and `create_record()`.

        :param model_path: The path to the model.
        :param cleanup: If true, remove temporary files after usage.
        :param wnid: The WordNet ID.
        :param wcategory: The WordNet category.
        :param scale: The scale of the object.

        :return The paths to each asset bundle as Path objects (from pathlib) and the path to the metadata record file as a Path object (from pathlib).
        """

        model_path = self.get_model_path(model_path)

        model_name = model_path.stem

        # Create the asset bundles.
        obj_path, is_new = self.fbx_to_obj(model_path)
        wrl_path = self.obj_to_wrl(model_path)
        obj_colliders_path = self.wrl_to_obj(wrl_path, model_name)
        copied_file_paths = self.move_files_to_unity_project(obj_colliders_path, model_path)
        prefab_path, report_path = self.create_prefab(f"{model_name}_colliders.obj", model_name, model_path.suffix)
        asset_bundle_paths = self.prefab_to_asset_bundle(prefab_path, model_name)

        # Parse the URLs.
        urls = self.get_local_urls(asset_bundle_paths)

        # Create the metadata record.
        record_path = self.create_record(model_name, wnid, wcategory, scale, urls)

        # Remove the temporary files.
        if cleanup:
            paths = [wrl_path, obj_colliders_path, prefab_path, report_path]
            paths.extend(copied_file_paths)
            if is_new:
                paths.append(obj_path)

            assert model_path not in paths

            for path in paths:
                if not path.exists():
                    continue
                path.unlink()

            # Remove all materials.
            materials_directory = self.get_resources_directory().joinpath("Materials")
            if materials_directory.exists():
                shutil.rmtree(str(materials_directory.resolve()))

            if not self._quiet:
                print("Removed temporary files.")

        if not self._quiet:
            print("DONE!")

        return asset_bundle_paths, record_path

    @staticmethod
    def get_model_path(model_path: Union[Path, str]) -> Path:
        """
        Check if the model path is valid.

        :param model_path: The path to the model. Can be a Path object, or a string representing the absolute file path.

        :return The path as a Path object if there are no problems.
        """

        if isinstance(model_path, str):
            model_path = Path(model_path)
        assert model_path.exists(), f"Model path doesn't exist: {model_path}"
        assert model_path.is_file(), f"Model path isn't a file: {model_path}"
        assert model_path.suffix in [".fbx", ".obj", ".prefab"], "Model file must be .fbx, .obj, or .prefab"

        return model_path

    def get_assets_directory(self) -> Path:
        """
        :return The path to `<home>/asset_bundle_creator/Assets/`
        """

        assets_directory = self._project_path.joinpath("Assets")
        assert assets_directory.exists(), f"Assets directory not found: {assets_directory.resolve()}"

        return assets_directory

    def get_resources_directory(self) -> Path:
        """
        :return The path to `<home>/asset_bundle_creator/Assets/Resources`
        """

        resources_directory = self.get_assets_directory().joinpath("Resources")
        assert resources_directory.exists(), f"Resources directory not found: {resources_directory.resolve()}"

        return resources_directory

    def get_base_unity_call(self) -> List[str]:
        """
        :return The call to launch Unity Editor silently in batchmode, execute something, and then quit.
        """

        return super().get_base_unity_call()

    def get_unity_project(self) -> Path:
        """
        Build the asset_bundle_creator Unity project.

        :return The path to the asset_bundle_creator Unity project.
        """

        unity_project_path = self.get_project_path()

        # If the project already exists, stop.
        if unity_project_path.exists():
            return unity_project_path

        if not self._quiet:
            print(f"Creating: {unity_project_path.resolve()}")

        call([str(self._unity_editor_path.resolve()),
              "-createProject",
              str(unity_project_path.resolve()),
              "-quit",
              "-batchmode"], env=self._env)
        assert unity_project_path.exists(), unity_project_path.resolve()
        if not self._quiet:
            print(f"Created new Unity project: {str(unity_project_path.resolve())}")
        # Add the .unitypackage to the new project.
        package_name = "asset_bundle_creator.unitypackage"
        filepath = pkg_resources.resource_filename(__name__, package_name)
        assert Path(filepath).exists(), filepath
        # Import the package.
        call([str(self._unity_editor_path.resolve()),
              "-projectPath",
              str(unity_project_path.resolve()),
              "-importPackage",
              filepath,
              "-quit",
              "-batchmode"], env=self._env)
        if not self._quiet:
            print(f"Imported {package_name} into the new project.")
        return unity_project_path

    @staticmethod
    def get_project_path() -> Path:
        """
        :return: The expected path of the Unity project.
        """

        return Path.home().joinpath("asset_bundle_creator")

    def fbx_to_obj(self, model_path: Path) -> Tuple[Path, bool]:
        """
        Convert a .fbx file to a .obj file with assimp

        :param model_path: The path to the model.

        :return The path to the new object, and True if it's a new file (False if it's the existing base file).
        """

        if model_path.suffix != ".fbx":
            assert model_path.suffix == ".obj"
            if not self._quiet:
                print("Model is already a .obj file. Skipping the conversion to .obj")
            return model_path, False

        if not self._quiet:
            print("Converting a .fbx file to .obj")

        # Create the .obj file.
        obj_filename = model_path.stem + ".obj"

        assimp = pkg_resources.resource_filename(__name__, self._binaries["assimp"])
        assert Path(assimp).exists(), assimp

        # Run assimp to create the .obj file.
        call([assimp,
              "export",
              str(model_path.resolve()),
              obj_filename],
             stdout=open(os.devnull, "wb"))

        obj_path = Path(obj_filename)
        assert obj_path.exists(), "Failed to convert .fbx to .obj"

        mtl_path = Path(obj_filename + ".mtl")
        if mtl_path.exists():
            mtl_path.unlink()
            if not self._quiet:
                print("Removed superfluous .obj.mtl file")

        return obj_path, True

    def obj_to_wrl(self, model_path: Path, vhacd_resolution: int = 8000000) -> Path:
        """
        Convert a .obj file to a .wrl file with testVHACD

        :param model_path: The path to the model.
        :param vhacd_resolution: The V-HACD voxel resolution. A higher number will create more accurate physics colliders, but it will take more time to initially create the asset bundle.

        :return The path to the .wrl file.
        """

        # Get the target .obj file.
        if model_path.suffix == ".obj":
            obj_path = str(model_path.resolve())
        else:
            obj_path = model_path.stem + ".obj"
        assert Path(obj_path).exists(), f"Target .obj doesn't exist: {obj_path}"

        wrl_filename = model_path.stem + ".wrl"
        if not self._quiet:
            print("Running V-HACD on a .obj file (this might take awhile).")

        # Run V-HACD.
        vhacd = pkg_resources.resource_filename(__name__, self._binaries["vhacd"])

        assert Path(vhacd).exists(), vhacd
        call([vhacd,
              "--input", obj_path,
              "--resolution", str(vhacd_resolution),
              "--output", wrl_filename],
             stdout=open(os.devnull, "wb"))

        assert Path(wrl_filename).exists(), "Failed to create .wrl file. " \
                                            "Check your original file to make sure that is 3D " \
                                            "(not just a flat plane) and isn't corrupted."

        if not self._quiet:
            print(f"Created: {wrl_filename}")

        # Remove the log, if any.
        if Path("log.txt").exists():
            os.remove("log.txt")

            if not self._quiet:
                print("Removed V-HACD log file.")

        # Remove the superfluous .obj file.
        if model_path.suffix != ".obj":
            os.remove(obj_path)

            if not self._quiet:
                print(f"Removed superfluous .obj file: {obj_path}")

        return Path(wrl_filename)

    def wrl_to_obj(self, wrl_filename: Path, model_name: str) -> Path:
        """
        Convert a .wrl file back into a .obj file with meshconv

        :param wrl_filename: The to the .wrl file.
        :param model_name: The name of the model (minus its file extension).

        :return The path to the .obj file.
        """

        assert wrl_filename.exists(), f"Missing .wrl file: {wrl_filename}"

        if not self._quiet:
            print("Converting .wrl to .obj")

        # Run meshconv.
        meshconv = pkg_resources.resource_filename(__name__, self._binaries["meshconv"])
        assert Path(meshconv).exists(), meshconv
        call([meshconv,
              str(wrl_filename.resolve()),
              "-c",
              "obj",
              "-o",
              f"{model_name}_colliders",
              "-sg"],
             stdout=open(os.devnull, "wb"))

        obj_path = Path(f"{model_name}_colliders.obj")
        assert obj_path.exists(), "Failed to create .obj file from .wrl file."

        if not self._quiet:
            print(f"Created {obj_path.resolve()} from .wrl file.")

        return obj_path

    def move_files_to_unity_project(self, obj_colliders: Optional[Path], model_path: Path, sub_directory: str = "") -> List[Path]:
        """
        Moves all required files to the Unity project.

        :param obj_colliders: The path to the colliders .obj file. May be None.
        :param sub_directory: Optional subdirectory to move the files to.
        :param model_path: The path to the model. Can be a Path object, or a string representing the absolute file path.

        :return A list of paths of files in the Unity project.
        """

        if obj_colliders is not None:
            assert obj_colliders.exists(), f"Colliders .obj file not found: {obj_colliders.resolve()}"

        resources_directory = self.get_resources_directory()

        if not self._quiet:
            print("Copying files into the Unity project.")

        mtl = model_path.parent.joinpath(Path(model_path.stem + ".mtl"))

        dests = []
        sources = [model_path, model_path.parent.joinpath("Materials"), model_path.parent.joinpath("Textures"), mtl]
        if obj_colliders is not None:
            sources.append(obj_colliders)

        # Open the mtl file and try to parse for textures
        if mtl.exists():
            mtl_txt = mtl.read_text()
            for mtl_line in mtl_txt.split("\n"):
                if ".jpg" in mtl_line:
                    tex_path = model_path.parent.joinpath(mtl_line.split(" ")[1])
                    assert tex_path.exists(), f"Missing texture: {tex_path}"
                    sources.append(tex_path)
        for src in sources:
            if src is None or not src.exists():
                continue
            if sub_directory == "":
                dest = resources_directory.joinpath(src.stem + src.suffix)
            else:
                dest = resources_directory.joinpath(sub_directory).joinpath(src.stem + src.suffix)
            # Copy to the destination.
            if src.is_file():
                if not dest.parent.exists():
                    Path(dest.parent).mkdir(parents=True)
                distutils.file_util.copy_file(str(src.resolve()), str(dest.resolve()))
            else:
                distutils.dir_util.copy_tree(str(src.resolve()), str(dest.resolve()))
            dests.append(dest)
        if not self._quiet:
            print("Copied files into the Unity project.")
        return dests

    def create_prefab(self, colliders: str, model_name: str, model_extension: str) -> Tuple[Path, Path]:
        """
        Create a prefab from the files existing in the Unity project folder.

        :param colliders: The colliders filename.
        :param model_name: The name of the model, minus its file extension.
        :param model_extension: The file extension of the model (e.g. ".obj").

        :return The path to the prefab and the path to the report (if any).
        """

        report = self.get_assets_directory().joinpath("report.txt")
        if report.exists():
            os.remove(str(report.resolve()))
            if not self._quiet:
                print("Removed old report.")

        # Create the prefab.
        if not self._quiet:
            print("Creating the prefab...")
        prefab_call = self._unity_call[:]
        prefab_call.extend(["-executeMethod",
                            "AssetBundleCreator.CreatePrefab",
                            "-filename=" + model_name,
                            "-modelname=" + model_name,
                            "-extension=" + model_extension,
                            "-colliders=" + colliders
                            ])
        call(prefab_call, env=self._env)
        prefab_path = self.get_resources_directory().joinpath(f"prefab/{model_name}.prefab")
        assert prefab_path.exists(), "Failed to create prefab."

        # Check the report.
        if report.exists():
            raise Exception(f"Created the prefab with errors: {report.read_text()}")

        if not self._quiet:
            print("Created the prefab.")

        return prefab_path, report

    def prefab_to_asset_bundle(self, prefab_path: Path, model_name: str, platforms: List[str] = None) -> List[Path]:
        """
        Given a .prefab, create asset bundles and write them to disk.

        :param prefab_path: The path to the .prefab file.
        :param model_name: The name of the model, minus its file extension.
        :param platforms: Platforms to build asset bundles for. Options: "windows", "osx", "linux". If None, build all.

        :return The paths to the asset bundles.
        """

        if platforms is None:
            platforms = ["windows", "osx", "linux"]

        assert prefab_path.exists(), f"Missing prefab: {prefab_path.resolve()}"

        if not self._quiet:
            print("Creating local asset bundles")
        asset_bundle_call = self._unity_call[:]
        platforms_call = ""
        for p in platforms:
            platforms_call += p + ","
        platforms_call = platforms_call[:-1]
        asset_bundle_call.extend(["-executeMethod",
                                  "AssetBundleCreator.BuildAssetBundle",
                                  "-modelname=" + model_name,
                                  "-platforms=" + platforms_call
                                  ])
        call(asset_bundle_call, env=self._env)
        new_asset_bundles_directory = self.get_assets_directory().joinpath("NewAssetBundles")
        new_asset_bundles_directory = new_asset_bundles_directory.joinpath(model_name)
        assert new_asset_bundles_directory.exists(), f"No asset bundles found: {new_asset_bundles_directory.resolve()}"

        paths = []

        # Iterate through all target platforms and build asset bundles.
        for platform_key in platforms:
            asset_bundle_platform = S3_TO_UNITY[platform_key]
            bundle_path = new_asset_bundles_directory.joinpath(asset_bundle_platform).joinpath(model_name)
            assert bundle_path.exists(), f"Missing asset bundle: {asset_bundle_platform}"
            paths.append(bundle_path)

        if not self._quiet:
            print("Created local asset bundles.")

        return paths

    @staticmethod
    def get_local_asset_bundle_path(model_name: str) -> Path:
        """
        :param model_name: The name of the model, minus its file extension.

        :return The expected path of the local asset bundle for this platform.
        """

        return Path.home().joinpath("asset_bundle_creator/Assets/NewAssetBundles").\
            joinpath(model_name + "/" + SYSTEM_TO_UNITY[platform.system()] + "/" + model_name)

    def create_record(self, model_name: str, wnid: int, wcategory: str, scale: float, urls: Dict[str, str], record: Optional[ModelRecord] = None, write_physics: bool = False) -> Path:
        """
        Create a local .json metadata record of the model.

        :param model_name: The name of the model.
        :param wnid: The WordNet ID.
        :param wcategory: The WordNet category.
        :param scale: The default scale of the object.
        :param urls: The finalized URLs (or local filepaths) of the assset bundles.
        :param record: A pre-written metadata record. If not None, it will override the other parameters.
        :param write_physics: If true, launch the build to write the physics quality. (This is optional).

        :return The path to the file with the metadata record.
        """

        # Write the record.
        if not self._quiet:
            print("Creating a record.")

        if record is None:
            record = ModelRecord()
            record.name = model_name
            record.wnid = f'n{wnid:08d}'
            record.wcategory = wcategory
            record.urls = urls
            record.scale = scale

        # Append asset bundle sizes.
        local_path = Path.home().joinpath("asset_bundle_creator/Assets/NewAssetBundles").joinpath(record.name)
        for os_dir in local_path.iterdir():
            if not os_dir.is_dir():
                continue
            asset_bundle_platform = UNITY_TO_SYSTEM[os_dir.stem]
            size = os_dir.joinpath(record.name).stat().st_size
            record.asset_bundle_sizes[asset_bundle_platform] = size

        # Assemble a dictionary of just the data that we don't need the Editor for.
        record_data = {"name": record.name,
                       "urls": record.urls,
                       "wnid": record.wnid,
                       "wcategory": record.wcategory,
                       "scale_factor": record.scale_factor,
                       "do_not_use": record.do_not_use,
                       "do_not_use_reason": record.do_not_use_reason,
                       "canonical_rotation": record.canonical_rotation,
                       "physics_quality": -1,
                       "asset_bundle_sizes": record.asset_bundle_sizes,
                       "container_colliders": []}

        # Serialize the record.
        record_data = json.dumps(record_data)
        # Remove the last } and replace it with , to keep serializing with Unity.
        record_data = record_data[:-1] + ","

        record_path = self.get_assets_directory().joinpath(model_name + ".json")
        record_path.write_text(record_data, encoding="utf-8")

        record_call = self._unity_call[:]
        record_call.extend(["-executeMethod",
                            "RecordCreator.WriteRecord",
                            "-modelname=" + model_name,
                            "-scale=" + str(scale)])
        call(record_call, env=self._env)

        # Test the record.
        try:
            json.loads(record_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raise Exception("Failed to deserialize: " + record_path.read_text(encoding="utf-8"))

        if not self._quiet:
            print("Wrote the record data to the disk.")

        if write_physics:
            self.write_physics_quality(record_path=record_path,
                                       asset_bundle_path=self.get_local_asset_bundle_path(model_name).resolve())

        return record_path

    @staticmethod
    def get_local_urls(asset_bundle_paths: List[Path]) -> Dict[str, str]:
        """
        Generate a dictionary of local URLs from the asset bundle paths.

        :param asset_bundle_paths: The asset bundle paths.

        :return A dictionary. Key = OS, Value = Path to the local file.
        """

        urls: Dict[str, str] = {}
        for ap in asset_bundle_paths:
            ap = "file:///" + str(ap.resolve()).replace("\\", "/")
            if "StandaloneWindows64" in ap:
                urls.update({"Windows": ap})
            elif "StandaloneOSX" in ap:
                urls.update({"Darwin": ap})
            elif "StandaloneLinux64" in ap:
                urls.update({"Linux": ap})
        return urls

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

    def create_many_asset_bundles(self, library_path: str, cleanup: bool = True, vhacd_resolution: int = 8000000) -> None:
        """
        Create asset bundles in batch from .obj or .fbx files already in: asset_bundle_creator/Assets/Resources/models
        This function will create collider .obj files if there aren't any already
        (it will look for a file named <model>_colliders.obj).

        :param library_path: The path to the library file.
        :param cleanup: If true, remove all temp files when done.
        :param vhacd_resolution: The V-HACD voxel resolution. A higher number will create more accurate physics colliders, but it will take more time to initially create the asset bundle.
        """

        # Create for each model that doesn't have colliders.
        models_dir = self.get_resources_directory().joinpath("models")
        for ext in [".obj", ".fbx"]:
            for f in models_dir.rglob(f"*{ext}"):
                if f.stem.endswith("_colliders"):
                    continue
                colliders_path = f.parent.joinpath(f"{f.stem}_colliders.obj")
                # Don't regenerate a colliders file if one already exists.
                if colliders_path.exists():
                    continue
                # Don't recreate models that already have prefabs.
                prefab_path = self.get_resources_directory().joinpath(f"prefab/{f.stem}.prefab")
                if prefab_path.exists():
                    continue
                # Create the colliders.
                wrl_path = self.obj_to_wrl(f, vhacd_resolution=vhacd_resolution)
                # Move the collider .obj to the correct directory.
                wrl_to_obj_path = self.wrl_to_obj(wrl_path, f.stem)
                distutils.file_util.move_file(str(wrl_to_obj_path.resolve()), str(colliders_path.resolve()))
                # Remove the .wrl file.
                wrl_path.unlink()

        # Create the asset bundles.
        record_call = self._unity_call[:]
        record_call.extend(["-executeMethod",
                            "AssetBundleCreator.CreateManyAssetBundles",
                            "-library=" + library_path,
                            "-internal_materials"])
        call(record_call)

        if cleanup:
            self.cleanup()

    def cleanup(self) -> None:
        """
        Delete all files from `~/asset_bundle_creator` with these extensions: .obj, .fbx, .mtl, .mat, .jpg, .prefab
        """

        root_dir = self.get_assets_directory()
        # Remove assets used to create asset bundles.
        for ext in [".obj", ".fbx", ".mtl", ".mat", ".jpg", ".prefab"]:
            for f in root_dir.rglob(f"*{ext}"):
                f.unlink()
        # Remove asset bundle junk.
        distutils.dir_util.remove_tree(str(self.get_assets_directory().joinpath("NewAssetBundles").resolve()))
        # Remove models junk.
        models_dir = self.get_resources_directory().joinpath("models")
        for d in models_dir.iterdir():
            if "placeholder" in d.stem:
                continue
            if d.is_file():
                d.unlink()
            else:
                distutils.dir_util.remove_tree(str(d.resolve()))
