from pathlib import Path
from typing import Union
from tdw.librarian import ModelRecord, ModelLibrarian
import json
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

    [For more information, read this.](../lessons/3d_models/custom_models.md)
    """

    def source_file_to_asset_bundles(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path],
                                     vhacd_resolution: int = 800000, internal_materials: bool = False,
                                     wnid: str = None, wcategory: str = None, scale_factor: float = 1,
                                     library_path: Union[str, Path] = None, cleanup: bool = True,
                                     write_physics_quality: bool = False, validate: bool = False) -> None:
        """
        Convert a source .obj or .fbx file into 3 asset bundle files (Windows, OS X, and Linux).

        This is equivalent to, *but significantly faster than*, a combination of:

        - `self.source_file_to_prefab()`
        - `self.prefab_to_asset_bundles()`
        - `self.create_record()`
        - `self.cleanup()`
        - `self.write_physics_quality()`
        - `self.validate()`

        Example source directory:

        ```
        source_file.obj
        source_file.mtl
        Textures/
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....Darwin/
        ........name
        ....Linux/
        ........name
        ....Windows/
        ........name
        ....record.json
        ....log.txt
        ```

        - `Darwin/name`, `Linux/name` and `Windows/name` are the platform-specific asset bundles.
        - `record.json` is a JSON dictionary of the `ModelRecord`.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.

        :param name: The name of the model. This can be the same as the source file name minus the extension.
        :param source_file: The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        :param internal_materials: If True, the visual materials of the model are located within the source file. If False, the materials are located in `Materials/` directory next to the source file.
        :param wnid: The WordNet ID of the model. Can be None.
        :param wcategory: The WordNet category of the model. Can be None.
        :param scale_factor: The model will be scaled by this factor.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `ModelLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        :param cleanup: If True, delete intermediary files such as the prefab in the `asset_bundle_creator` Unity Editor project.
        :param write_physics_quality: If True, launch a controller and build to calculate the hull collider accuracy. Write the result to `output_directory/record.json` and to `library_path` if `library_path` is not None.
        :param validate: If True, launch a controller and build to validate the model, checking it for any errors. Write the result to `output_directory/record.json` and to `library_path` if `library_path` is not None.
        """

        args = AssetBundleCreator._get_source_destination_args(name=name, source=source_file, destination=output_directory)
        args.extend([f"-vhacd_resolution={vhacd_resolution}",
                     f"-scale_factor={scale_factor}"])
        for value, flag in zip([wnid, wcategory], ["wnid", "wcategory"]):
            if value is not None:
                args.append(f'-{flag}="{value}"')
        args = AssetBundleCreatorBase._add_library_path(args=args, library_path=library_path)
        for value, flag in zip([internal_materials, cleanup], ["-internal_materials", "-cleanup"]):
            if value:
                args.append(flag)
        self.call_unity(method="SourceFileToAssetBundles", args=args)
        self._print_log(output_directory=output_directory)
        # Write physics quality.
        if isinstance(output_directory, str):
            record_path = Path(output_directory).joinpath("record.json")
        elif isinstance(output_directory, Path):
            record_path = output_directory.joinpath("record.json")
        else:
            raise Exception(output_directory)
        if write_physics_quality:
            self.write_physics_quality(name=name, record_path=record_path, library_path=library_path)
        if validate:
            self.validate(name=name, record_path=record_path, library_path=library_path)

    def source_directory_to_asset_bundles(self, source_directory: Union[str, Path],
                                          output_directory: Union[str, Path], library_description: str = None,
                                          vhacd_resolution: int = 800000, internal_materials: bool = False) -> None:
        """
        Convert a directory of source .fbx and/or .obj models to asset bundles.

        Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

        Example `source_directory`:

        ```
        source_directory/
        ....model_0/
        ........model_0.obj
        ........model_0.mtl
        ........Textures/
        ....model_1/
        ........model_1.obj
        ........model_1.mtl
        ........Textures/
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....model_0/
        ........Darwin/
        ............model_0
        ........Linux/
        ............model_0
        ........Windows/
        ............model_0
        ........record.json
        ........log.txt
        ....model_1/
        ........Darwin/
        ............model_1
        ........Linux/
        ............model_1
        ........Windows/
        ............model_1
        ........record.json
        ........log.txt
        ```

        - `Darwin/model_0`, `Linux/model_0`, etc. are the platform-specific asset bundles.
        - `record.json` is a JSON dictionary of the `ModelRecord`.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.

        Note: This method does *not* call `self.write_physics_quality()` or `self.validate()`.

        :param source_directory: The root directory of the source files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param library_description: An optional description of the `ModelLibrarian` that will be included in the `library.json` file.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        :param internal_materials: If True, the visual materials of the models are located within the source file. If False, the materials are located in `Materials/` directory next to each source file.
        """

        if isinstance(source_directory, Path):
            src = str(source_directory.resolve())
        else:
            src = source_directory
        if isinstance(output_directory, Path):
            dst = str(output_directory.resolve())
        else:
            dst = output_directory
        args = [f'-source_directory="{src}"',
                f'-output_directory="{dst}"',
                f'-vhacd_resolution={vhacd_resolution}']
        if library_description is not None:
            args.append(f'-library_description="{library_description}"')
        if internal_materials:
            args.append("-internal_materials")
        # Execute the call.
        self.call_unity(method="SourceDirectoryToAssetBundles", args=args)

    def source_file_to_prefab(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path],
                              vhacd_resolution: int = None, internal_materials: bool = False) -> None:
        """
        Convert a source .obj or .fbx file into a .prefab file. Call this method when you intend to modify the .prefab file by hand before building asset bundles, e.g.:

        1. `self.source_file_to_prefab()`
        2. Edit .prefab file
        3. `self.prefab_to_asset_bundles()`

        Example source directory:

        ```
        source_file.obj
        source_file.mtl
        Textures/
        ```

        Example output:

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

        :param name: The name of the model. This can be the same as the source file name minus the extension. This will be the name of the .prefab file.
        :param source_file: The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        :param internal_materials: If True, the visual materials of the model are located within the source file. If False, the materials are located in `Materials/` directory next to the source file.
        """

        args = AssetBundleCreator._get_source_destination_args(name=name, source=source_file, destination=output_directory)
        if vhacd_resolution is not None:
            args.append(f"-vhacd_resolution={vhacd_resolution}")
        if internal_materials:
            args.append("-internal_materials")
        # Execute the call.
        self.call_unity(method="SourceFileToPrefab", args=args)
        self._print_log(output_directory=output_directory)

    def create_record(self, name: str, output_directory: Union[str, Path],
                      wnid: str = None, wcategory: str = None, scale_factor: float = 1,
                      library_path: Union[str, Path] = None) -> None:
        """
        Create a model record and save it to disk. This requires asset bundles of the model to already exist.

        The record will be saved to `output_directory/record.json`.

        :param name: The name of the model (matches the asset bundle file names).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param wnid: The WordNet ID of the model. Can be None.
        :param wcategory: The WordNet category of the model. Can be None.
        :param scale_factor: The model will be scaled by this factor.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `ModelLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        """

        if isinstance(output_directory, Path):
            dst = str(output_directory.resolve())
        else:
            dst = output_directory
        args = [f'-name="{name}"',
                f"-source=temp",
                f'-output_directory="{dst}"']
        for value, flag in zip([wnid, wcategory, scale_factor], ["wnid", "wcategory", "scale_factor"]):
            if value is not None:
                args.append(f'-{flag}="{value}"')
        args = AssetBundleCreatorBase._add_library_path(args=args, library_path=library_path)
        # Execute the call.
        self.call_unity(method="CreateRecord", args=args)
        self._print_log(output_directory=output_directory)

    def write_physics_quality(self, name: str, record_path: Union[str, Path] = None,
                              library_path: Union[str, Path] = None) -> None:
        """
        Append the physics quality data to the temporary record file.
        This is an optional record field that records the percentage of the model encapsulated by colliders.

        :param name: The model name.
        :param record_path: If not None, this is the path to the `ModelRecord` .json file, which will be updated.
        :param library_path: If not None, this is the path to an existing `ModelLibrarian` .json file, which will be updated.
        """

        # Get the record.
        if not self._quiet:
            print("Writing physics quality...")
        record: ModelRecord = AssetBundleCreator._get_record(name=name, record_path=record_path,
                                                             library_path=library_path)
        # Run the test.
        c = Controller(check_version=False)
        v = ModelVerifier()
        v.set_tests(name=record.name, source=record, model_report=False, missing_materials=False, physics_quality=True)
        c.add_ons.append(v)
        c.communicate([])
        while not v.done:
            c.communicate([])
        c.communicate({"$type": "terminate"})
        c.socket.close()
        # Write the physics quality.
        record.physics_quality = float(v.reports[0])
        if not self._quiet:
            print(f"Physics quality: {record.physics_quality}")
        self._set_record(record=record, record_path=record_path, library_path=library_path)

    def validate(self, name: str, record_path: Path, library_path: Path) -> None:
        """
        Validate the asset bundle.

        :param name: The model name.
        :param record_path: If not None, this is the path to the `ModelRecord` .json file, which will be updated.
        :param library_path: If not None, this is the path to an existing `ModelLibrarian` .json file, which will be updated.
        """

        if not self._quiet:
            print("Validating asset bundle...")
        record: ModelRecord = AssetBundleCreator._get_record(name=name, record_path=record_path,
                                                             library_path=library_path)
        c = Controller(check_version=False)
        v = ModelVerifier()
        v.set_tests(name=record.name, source=record, model_report=True, missing_materials=True, physics_quality=False)
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
            if not self._quiet:
                print(output)
            record.do_not_use = True
            record.do_not_use_reason = "\n".join(v.reports)
        else:
            if not self._quiet:
                print("OK!")
        self._set_record(record=record, record_path=record_path, library_path=library_path)

    def get_creator_class_name(self) -> str:
        return "ModelCreatorLauncher"

    @staticmethod
    def _get_record(name: str, record_path: Union[str, Path] = None,
                    library_path: Union[str, Path] = None) -> ModelRecord:
        """
        :param name: The model name.
        :param record_path: The path to a `ModelRecord` .json file.
        :param library_path: The path to a `ModelLibrarian` .json file.

        :return: A `ModelRecord`.
        """

        if record_path is not None:
            if isinstance(record_path, str):
                path = Path(record_path)
            elif isinstance(record_path, Path):
                path = record_path
            else:
                raise Exception(record_path)
            return ModelRecord(json.loads(path.read_text(encoding="utf-8")))
        elif library_path is None:
            if isinstance(library_path, str):
                model_librarian = ModelLibrarian(library_path)
            elif isinstance(library_path, Path):
                model_librarian = ModelLibrarian(str(library_path.resolve()))
            else:
                raise Exception(library_path)
            record = model_librarian.get_record(name)
            if record is None:
                raise Exception(f"Failed to get record named {name} from {library_path}")
            else:
                return record
        else:
            raise Exception("Failed to write physics quality because record_path and library_path are None. "
                            "At least one of these needs to have a value.")

    def _set_record(self, record: ModelRecord, record_path: Union[str, Path] = None,
                    library_path: Union[str, Path] = None) -> None:
        """
        :param record: The `ModelRecord`.
        :param record_path: The path to a `ModelRecord` .json file.
        :param library_path: The path to a `ModelLibrarian` .json file.
        """

        # Update the record.
        if record_path is not None:
            if isinstance(record_path, str):
                Path(record_path).write_text(json.dumps(record.__dict__, indent=2), encoding="utf-8")
            elif isinstance(record_path, Path):
                record_path.write_text(json.dumps(record.__dict__, indent=2), encoding="utf-8")
            if not self._quiet:
                print(f"Updated {record_path}")
        # Update the librarian.
        if library_path is not None:
            if isinstance(library_path, str):
                model_librarian = ModelLibrarian(library_path)
            elif isinstance(library_path, Path):
                model_librarian = ModelLibrarian(str(library_path.resolve()))
            else:
                raise Exception(library_path)
            overwrite = model_librarian.get_record(record.name) is not None
            model_librarian.add_or_update_record(record=record, overwrite=overwrite, write=True)
            if not self._quiet:
                print(f"Updated {library_path}")
