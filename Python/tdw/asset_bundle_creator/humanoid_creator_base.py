from abc import ABC
from typing import Union
from pathlib import Path
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.asset_bundle_creator.asset_bundle_creator import AssetBundleCreator


class HumanoidCreatorBase(AssetBundleCreator, ABC):
    """
    Abstract base class for creating humanoids and humanoid animations.
    """

    @final
    def source_file_to_asset_bundles(self, name: str, source_file: Union[str, Path], output_directory: Union[str, Path]) -> None:
        """
        Convert a source file into 3 asset bundle files (Windows, OS X, and Linux).

        :param name: The name of the animation.
        :param source_file: The path to the source file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created.
        """

        args = HumanoidCreatorBase._get_source_destination_args(name=name, source=source_file, destination=output_directory)
        self.call_unity(method="SourceFileToAssetBundles",
                        args=args,
                        log_path=AssetBundleCreator._get_log_path(output_directory))

    @final
    def source_directory_to_asset_bundles(self, source_directory: Union[str, Path], output_directory: Union[str, Path],
                                          library_description: str = None, overwrite: bool = False, continue_on_error: bool = True,
                                          search_pattern: str = None, cleanup: bool = True) -> None:
        """
        Convert a directory of source files to asset bundles.

        Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

        :param source_directory: The root directory of the source files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param output_directory: The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html).
        :param library_description: An optional description of the `ModelAnimationLibrarian` that will be included in the `library.json` file.
        :param overwrite: If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents.
        :param continue_on_error: If True, continue generating asset bundles even if there is a problem with one file. If False, stop the process if there's an error.
        :param search_pattern: A search pattern for files, for example `"*.fbx"`. All subdirectories will be recursively searched.
        :param cleanup: If True, delete intermediary files such as the prefabs in the `asset_bundle_creator` Unity Editor project.
        """

        args = [f'-source_directory="{TDWUtils.get_string_path(source_directory)}"',
                f'-output_directory="{TDWUtils.get_string_path(output_directory)}"']
        args = AssetBundleCreator._add_library_args(args=args, library_description=library_description)
        if search_pattern is not None:
            args.append(f'-search_pattern="{search_pattern}"')
        if overwrite:
            args.append("-overwrite")
        if continue_on_error:
            args.append("-continue_on_error")
        if cleanup:
            args.append("-cleanup")
        self.call_unity(method="SourceDirectoryToAssetBundles",
                        args=args,
                        log_path=TDWUtils.get_path(output_directory).joinpath("progress.txt"))
