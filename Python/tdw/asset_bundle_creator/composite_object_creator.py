from pathlib import Path
from typing import Union
from tdw.asset_bundle_creator.asset_bundle_creator import AssetBundleCreator


class CompositeObjectCreator(AssetBundleCreator):
    """
    Create asset bundles of objects from a .urdf file.

    This class should very rarely be used! In most cases, you should use [`RobotCreator`](robot_creator.md) instead.

    This class should only be used for *non*-robot .urdf files such as PartNet Mobility files.
    """

    def source_file_to_asset_bundles(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path],
                                     vhacd_resolution: int = 800000, wnid: str = None, wcategory: str = None,
                                     cleanup: bool = True) -> None:
        """
        Convert a source .urdf file into 3 asset bundle files (Windows, OS X, and Linux).

        This is equivalent to, *but significantly faster than*, a combination of:

        - `self.source_file_to_prefab()`
        - `self.prefab_to_asset_bundles()`
        - `self.cleanup()`

        Example source directory:

        ```
        mobility.urdf
        textured_objs/
        ....original-1.obj
        ....original-1.mtl
        .... (etc.)
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....Darwin/
        ........mobility
        ....Linux/
        ........mobility
        ....Windows/
        ........mobility
        ....log.txt
        ....model.json
        ```

        - `Darwin/mobility`, `Linux/mobility` and `Windows/mobility` are the platform-specific asset bundles.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
        - `model.json` is a JSON dump of the converted URDF data and mesh paths.

        :param name: The name of the model. This can be the same as the source file name minus the extension.
        :param source_file: The path to the source .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        :param wnid: The WordNet ID of the model. Can be None.
        :param wcategory: The WordNet category of the model. Can be None.
        :param cleanup: If True, delete intermediary files such as the prefab in the `asset_bundle_creator` Unity Editor project.
        """

        args = CompositeObjectCreator._get_source_destination_args(name=name, source=source_file, destination=output_directory)
        args.append(f"-vhacd_resolution={vhacd_resolution}")
        for value, flag in zip([wnid, wcategory], ["wnid", "wcategory"]):
            if value is not None:
                args.append(f'-{flag}="{value}"')
        if cleanup:
            args.append("-cleanup")
        self.call_unity(method="SourceFileToAssetBundles",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    def source_file_to_prefab(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path],
                              vhacd_resolution: int = None) -> None:
        """
        Convert a source .urdf file into a .prefab file. Call this method when you intend to modify the .prefab file by hand before building asset bundles, e.g.:

        1. `self.source_file_to_prefab()`
        2. Edit .prefab file
        3. `self.prefab_to_asset_bundles()`

        Example source directory:

        ```
        mobility.urdf
        textured_objs/
        ....original-1.obj
        ....original-1.mtl
        .... (etc.)
        ```

        Example output:

        ```
        ~/asset_bundle_creator/
        ....Assets/
        ........prefabs/
        ............mobility.prefab
        ........source_files/
        ............mobility/
        ................mobility.obj
        ```

        :param name: The name of the model. This can be the same as the source file name minus the extension. This will be the name of the .prefab file.
        :param source_file: The path to the source .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        :param vhacd_resolution: The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes.
        """

        args = CompositeObjectCreator._get_source_destination_args(name=name, source=source_file, destination=output_directory)
        if vhacd_resolution is not None:
            args.append(f"-vhacd_resolution={vhacd_resolution}")
        # Execute the call.
        self.call_unity(method="SourceFileToPrefab",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    def get_creator_class_name(self) -> str:
        return "CompositeObjectCreator"
