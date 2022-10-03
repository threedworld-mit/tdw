from pathlib import Path
from typing import Union
import json
from tdw.librarian import ModelRecord, ModelLibrarian
from tdw.asset_bundle_creator.asset_bundle_creator import AssetBundleCreator
from tdw.add_ons.model_verifier.model_verifier import ModelVerifier
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


class ModelCreator(AssetBundleCreator):
    """
    Given a .fbx file or a .obj file, and (optionally) Materials and/or Textures folder adjacent to that file, create asset bundles for Windows, OS X, and Linux.

    Usage:

    ```python
    from tdw.asset_bundle_creator.model_creator import ModelCreator
    from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

    a = ModelCreator()
    a.source_file_to_asset_bundles(name="cube",
                                   source_file="cube.fbx",
                                   output_directory=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("cube"))
    ```

    [For more information, read this.](../../lessons/custom_models/custom_models.md)
    """

    def source_file_to_asset_bundles(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path],
                                     vhacd_resolution: int = 800000, internal_materials: bool = False,
                                     wnid: str = None, wcategory: str = None, scale_factor: float = 1,
                                     library_path: Union[str, Path] = None, library_description: str = None,
                                     cleanup: bool = True, write_physics_quality: bool = False, validate: bool = False) -> None:
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
        model.obj
        model.mtl
        Textures/
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....Darwin/
        ........model
        ....Linux/
        ........model
        ....Windows/
        ........model
        ....record.json
        ....log.txt
        library.json
        ```

        - `Darwin/model`, `Linux/model` and `Windows/model` are the platform-specific asset bundles.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
        - `record.json` is a serialized `ModelRecord`.
        - `library.json` is a serialized `ModelLibrarian`. It will only be added/set if the optional `library_path` is set.

        :param name: The name of the model. This can be the same as the source file name minus the extension.
        :param source_file: The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        :param internal_materials: If True, the visual materials of the model are located within the source file. If False, the materials are located in `Materials/` directory next to the source file.
        :param wnid: The WordNet ID of the model. Can be None.
        :param wcategory: The WordNet category of the model. Can be None.
        :param scale_factor: The model will be scaled by this factor.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `ModelLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        :param library_description: A description of the library. Ignored if `library_path` is None.
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
        args = AssetBundleCreator._add_library_args(args=args,
                                                    library_path=library_path,
                                                    library_description=library_description)
        for value, flag in zip([internal_materials, cleanup], ["-internal_materials", "-cleanup"]):
            if value:
                args.append(flag)
        self.call_unity(method="SourceFileToAssetBundles",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))
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

    def source_directory_to_asset_bundles(self, source_directory: Union[str, Path],  output_directory: Union[str, Path],
                                          library_description: str = None,  vhacd_resolution: int = 800000,
                                          internal_materials: bool = False, overwrite: bool = False,
                                          continue_on_error: bool = True, search_pattern: str = None,
                                          cleanup: bool = True) -> None:
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
        :param overwrite: If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents.
        :param continue_on_error: If True, continue generating asset bundles even if there is a problem with one model. If False, stop the process if there's an error.
        :param search_pattern: A search pattern for files, for example `"*.obj"`. All subdirectories will be recursively searched.
        :param cleanup: If True, delete intermediary files such as the prefabs in the `asset_bundle_creator` Unity Editor project.
        """

        args = [f'-source_directory="{TDWUtils.get_string_path(source_directory)}"',
                f'-output_directory="{TDWUtils.get_string_path(output_directory)}"',
                f'-vhacd_resolution={vhacd_resolution}']
        args = AssetBundleCreator._add_library_args(args=args, library_description=library_description)
        if search_pattern is not None:
            args.append(f'-search_pattern="{search_pattern}"')
        if internal_materials:
            args.append("-internal_materials")
        if overwrite:
            args.append("-overwrite")
        if continue_on_error:
            args.append("-continue_on_error")
        if cleanup:
            args.append("-cleanup")
        self.call_unity(method="SourceDirectoryToAssetBundles",
                        args=args,
                        log_path=TDWUtils.get_path(output_directory).joinpath("progress.txt"))

    def metadata_file_to_asset_bundles(self, metadata_path: Union[str, Path], output_directory: Union[str, Path],
                                       library_description: str = None, vhacd_resolution: int = 800000,
                                       internal_materials: bool = False, overwrite: bool = False,
                                       continue_on_error: bool = True, cleanup: bool = True) -> None:
        """
        Given a metadata .csv file within an output directory, generate asset bundles.

        This is similar to `self.source_directory_to_asset_bundles()` but it reads a single .csv file instead of a directory structure, which allows you to specify record data per source file.

        Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

        Example metadata .csv file:

        ```
        name,wnid,wcategory,scale_factor,path
        model_0,n04148054,scissors,1,source_directory/model_0/model_0.obj
        model_1,n03056701,coaster,1,source_directory/model_1/model_1.obj
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

        :param metadata_path: The path to the metadata file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param library_description: An optional description of the `ModelLibrarian` that will be included in the `library.json` file.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        :param internal_materials: If True, the visual materials of the models are located within the source file. If False, the materials are located in `Materials/` directory next to each source file.
        :param overwrite: If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents.
        :param continue_on_error: If True, continue generating asset bundles even if there is a problem with one model. If False, stop the process if there's an error.
        :param cleanup: If True, delete intermediary files such as the prefabs in the `asset_bundle_creator` Unity Editor project.
        """

        args = [f'-metadata_path={TDWUtils.get_string_path(metadata_path)}',
                f'-output_directory="{TDWUtils.get_string_path(output_directory)}"',
                f'-vhacd_resolution={vhacd_resolution}']
        args = AssetBundleCreator._add_library_args(args=args, library_description=library_description)
        if internal_materials:
            args.append("-internal_materials")
        if overwrite:
            args.append("-overwrite")
        if continue_on_error:
            args.append("-continue_on_error")
        if cleanup:
            args.append("-cleanup")
        self.call_unity(method="MetadataFileToAssetBundles",
                        args=args,
                        log_path=TDWUtils.get_path(output_directory).joinpath("progress.txt"))

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
        self.call_unity(method="SourceFileToPrefab",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    def create_record(self, name: str, output_directory: Union[str, Path],
                      wnid: str = None, wcategory: str = None, scale_factor: float = 1,
                      library_path: Union[str, Path] = None, library_description: str = None) -> None:
        """
        Create a model record and save it to disk. This requires asset bundles of the model to already exist:

        ```
        output_directory/
        ....Darwin/
        ........model
        ....Linux/
        ........model
        ....Windows/
        ........model
        ....log.txt
        ```

        Result:

        ```
        output_directory/
        ....Darwin/
        ........model
        ....Linux/
        ........model
        ....Windows/
        ........model
        ....record.json
        ....log.txt
        library.json
        ```

        - `record.json` is a serialized `ModelRecord`.
        - `library.json` is a serialized `ModelLibrarian`. It will only be added/set if the optional `library_path` is set.

        :param name: The name of the model (matches the asset bundle file names).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param wnid: The WordNet ID of the model. Can be None.
        :param wcategory: The WordNet category of the model. Can be None.
        :param scale_factor: The model will be scaled by this factor.
        :param library_path: If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `ModelLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`.
        :param library_description: A description of the library. Ignored if `library_path` is None.
        """

        args = [f'-name="{name}"',
                f"-source=temp",
                f'-output_directory="{TDWUtils.get_string_path(output_directory)}"']
        for value, flag in zip([wnid, wcategory, scale_factor], ["wnid", "wcategory", "scale_factor"]):
            if value is not None:
                args.append(f'-{flag}="{value}"')
        args = AssetBundleCreator._add_library_args(args=args,
                                                    library_path=library_path,
                                                    library_description=library_description)
        # Execute the call.
        self.call_unity(method="CreateRecord",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

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
        if not self.quiet:
            print("Writing physics quality...")
        record: ModelRecord = ModelCreator._get_record(name=name, record_path=record_path, library_path=library_path)
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
        if not self.quiet:
            print(f"Physics quality: {record.physics_quality}")
        self._set_record(record=record, record_path=record_path, library_path=library_path)

    def validate(self, name: str, record_path: Path = None, library_path: Path = None) -> None:
        """
        Validate the asset bundle.

        :param name: The model name.
        :param record_path: If not None, this is the path to the `ModelRecord` .json file, which will be updated.
        :param library_path: If not None, this is the path to an existing `ModelLibrarian` .json file, which will be updated.
        """

        if not self.quiet:
            print("Validating asset bundle...")
        record: ModelRecord = ModelCreator._get_record(name=name, record_path=record_path, library_path=library_path)
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
            if not self.quiet:
                print(output)
            record.do_not_use = True
            record.do_not_use_reason = "\n".join(v.reports)
        else:
            if not self.quiet:
                print("OK!")
        self._set_record(record=record, record_path=record_path, library_path=library_path)

    def get_creator_class_name(self) -> str:
        return "ModelCreator"

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
            return ModelRecord(json.loads(TDWUtils.get_path(record_path).read_text(encoding="utf-8")))
        elif library_path is not None:
            model_librarian = ModelLibrarian(TDWUtils.get_string_path(library_path))
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
            TDWUtils.get_path(record_path).write_text(json.dumps(record.__dict__, indent=2), encoding="utf-8")
            if not self.quiet:
                print(f"Updated {record_path}")
        # Update the librarian.
        if library_path is not None:
            model_librarian = ModelLibrarian(TDWUtils.get_string_path(library_path))
            overwrite = model_librarian.get_record(record.name) is not None
            model_librarian.add_or_update_record(record=record, overwrite=overwrite, write=True)
            if not self.quiet:
                print(f"Updated {library_path}")
