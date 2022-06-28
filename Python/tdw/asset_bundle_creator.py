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
        self.call_unity(method="SourceDirectoryToAssetBundles", args=args)

    def source_file_to_prefab(self, source_file: Union[str, Path], output_directory: Union[str, Path],
                              vhacd_resolution: int = None, internal_materials: bool = False) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        if vhacd_resolution is not None:
            args.append(f"-vhacd_resolution={vhacd_resolution}")
        if internal_materials:
            args.append("-internal_materials")
        # Execute the call.
        self.call_unity(method="SourceFileToPrefab", args=args)

    def prefab_to_asset_bundles(self, source_file: Union[str, Path]) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination="")
        # Execute the call.
        self.call_unity(method="PrefabToAssetBundles", args=args)

    def move_asset_bundles(self, source_file: Union[str, Path], output_directory: Union[str, Path]) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        # Execute the call.
        self.call_unity(method="MoveAssetBundles", args=args)

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
        self.call_unity(method="CreateRecord", args=args)

    def cleanup(self, source_file: Union[str, Path], output_directory: Union[str, Path]) -> None:
        args = AssetBundleCreator._get_src_dst(source=source_file, destination=output_directory)
        args.append("-cleanup")
        # Execute the call.
        self.call_unity(method="Cleanup", args=args)

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

    def get_creator_class_name(self) -> str:
        return "ModelCreatorLauncher"

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
