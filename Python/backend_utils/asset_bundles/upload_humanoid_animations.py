from pathlib import Path
from json import loads
from argparse import ArgumentParser
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidAnimationRecord
from tdw.asset_bundle_creator.animation_creator import AnimationCreator
from tdw.dev.asset_bundles import AssetBundles


def upload(asset_bundles_directory: Path) -> None:
    """
    Upload animation asset bundles.

    :param asset_bundles_directory: The root directory of these asset bundles and the location of `record.json`.
    """

    record_path = asset_bundles_directory.joinpath("record.json")
    if not record_path.exists():
        print(f"File not found: {record_path}")
        return
    lib = HumanoidAnimationLibrarian(args.library)
    AssetBundles.upload_asset_bundles(name=asset_bundles_directory.name,
                                      asset_bundles_directory=str(asset_bundles_directory.resolve()),
                                      librarian=lib,
                                      record=HumanoidAnimationRecord(loads(record_path.read_text(encoding="utf-8"))),
                                      quiet=False,
                                      write=True)


parser = ArgumentParser()
parser.add_argument("source",
                    type=str,
                    help="Either the root source directory of the animation files, or a single .anim file.")
parser.add_argument("--output_directory",
                    type=str,
                    help="The root output directory for the local asset bundles.")
parser.add_argument("--upload", action="store_true", help="If included, upload to the S3 bucket and update the records.")
parser.add_argument("--library", type=str, default="humanoid_animations.json", help="The humanoid animation library.")
args = parser.parse_args()
source: Path = Path(args.source)
output_directory: Path = Path(args.output_directory)
creator = AnimationCreator()
# Generate asset bundles from a single file.
if source.is_file():
    name = source.name.split(".")[0]
    creator.source_file_to_asset_bundles(name=name,
                                         source_file=source,
                                         output_directory=output_directory)
    upload(output_directory)
# Generate asset bundles from a source directory.
else:
    creator.source_directory_to_asset_bundles(source_directory=source,
                                              output_directory=output_directory)
    # Get the asset bundles.
    for directory in output_directory.iterdir():
        if directory.is_dir():
            upload(directory)
