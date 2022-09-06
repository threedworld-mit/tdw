from typing import Union
from pathlib import Path
from tdw.asset_bundle_creator_base import AssetBundleCreatorBase


class AnimationCreator(AssetBundleCreatorBase):
    """
    Create animation asset bundles from .anim or .fbx files.
    """

    def get_creator_class_name(self) -> str:
        return "AnimationCreator"

    def source_file_to_asset_bundles(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path]) -> None:
        """
        Convert a source .anim or .fbx file into 3 asset bundle files (Windows, OS X, and Linux).

        Example source directory:

        ```
        animation.anim
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....Darwin/
        ........animation
        ....Linux/
        ........animation
        ....Windows/
        ........animation
        ....log.txt
        ....record.json
        ```

        - `Darwin/animation`, `Linux/animation` and `Windows/animation` are the platform-specific asset bundles.
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
        - `record.json` is a serialized record.

        :param name: The name of the animation.
        :param source_file: The path to the source file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        """

        args = AnimationCreator._get_source_destination_args(name=name, source=source_file, destination=output_directory)
        self.call_unity(method="SourceFileToAssetBundles",
                        args=args,
                        log_path=AssetBundleCreatorBase._get_log_path(output_directory))

    def source_directory_to_asset_bundles(self, source_directory: Union[str, Path], output_directory: Union[str, Path],
                                          overwrite: bool = False, continue_on_error: bool = True,
                                          search_pattern: str = None) -> None:
        """
        Convert a directory of source .fbx and/or .obj models to asset bundles.

        Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

        Example `source_directory`:

        ```
        source_directory/
        ....animation_0.anim
        ....animation_1.anim
        ```

        Example `output_directory`:

        ```
        output_directory/
        ....animation_0/
        ........Darwin/
        ............animation_0
        ........Linux/
        ............animation_0
        ........Windows/
        ............animation_0
        ........record.json
        ........log.txt
        ....animation_1/
        ........Darwin/
        ............animation_1
        ........Linux/
        ............animation_1
        ........Windows/
        ............animation_1
        ........record.json
        ........log.txt
        ```

        - `Darwin/animation_0`, `Linux/animation_0`, etc. are the platform-specific asset bundles.
        - `record.json` is a JSON dictionary of the  record
        - `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.

        :param source_directory: The root directory of the source files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param overwrite: If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents.
        :param continue_on_error: If True, continue generating asset bundles even if there is a problem with one model. If False, stop the process if there's an error.
        :param search_pattern: A search pattern for files, for example `"*.obj"`. All subdirectories will be recursively searched.
        """

        args = [f'-source_directory="{AssetBundleCreatorBase.get_string_path(source_directory)}"',
                f'-output_directory="{AssetBundleCreatorBase.get_string_path(output_directory)}"']
        if search_pattern is not None:
            args.append(f'-search_pattern="{search_pattern}"')
        if overwrite:
            args.append("-overwrite")
        if continue_on_error:
            args.append("-continue_on_error")
        self.call_unity(method="SourceDirectoryToAssetBundles",
                        args=args,
                        log_path=AssetBundleCreatorBase.get_path(output_directory).joinpath("progress.txt"))
