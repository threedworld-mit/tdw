from json import loads
from pathlib import Path
from argparse import ArgumentParser
from typing import Optional
import boto3
from tdw.asset_bundle_creator.robot_creator import RobotCreator
from tdw.librarian import RobotLibrarian, RobotRecord
from tdw.dev.asset_bundles import AssetBundles

"""
Upload each robot in `manifest.json`.
"""


if __name__ == "__main__":
    # Add a command line argument to upload.
    parser = ArgumentParser()
    parser.add_argument("--upload", action="store_true",
                        help="Create asset bundles from existing prefabs, add the records to the metadata library, "
                             "and upload to the S3 server.")
    parser.add_argument("--output_directory",
                        type=str,
                        default="D:/robot_asset_bundles",
                        help="Output directory for asset bundles.")
    parser.add_argument("--update",
                        type=str,
                        default="",
                        help="Update an existing robot from a prefab.")
    args = parser.parse_args()
    lib = RobotLibrarian()
    s3 = boto3.resource('s3')
    rc = RobotCreator()
    if args.update != "":
        name: str = args.up
        output_directory = Path(args.output_directory).joinpath(name)
        rc.prefab_to_asset_bundles(name=name, output_directory=output_directory)
        AssetBundles.upload_asset_bundles(name=name,
                                          asset_bundles_directory=str(output_directory.resolve()),
                                          librarian=lib,
                                          url_infix="robot",
                                          write=True,
                                          quiet=False)
    else:
        bucket = "tdw-public"
        # Load the manifest.
        manifest = loads(Path("manifest.json").read_text(encoding="utf-8"))
        # Create each robot.
        for name in manifest:
            print(name)
            output_directory = Path(args.output_directory).joinpath(name)
            robot = manifest[name]
            url: str = robot["url"]
            description_infix: Optional[str] = None
            if "description_infix" in robot:
                description_infix = robot["description_infix"]
            if "immovable" in robot:
                immovable: bool = robot["immovable"]
            else:
                immovable: bool = True
            if "branch" in robot:
                branch = robot["branch"]
            else:
                branch = "master"
            # Create asset bundles to an existing prefab and upload them to the S3 server.
            if args.upload:
                # Create the asset bundles.
                rc.prefab_to_asset_bundles(name=name, output_directory=output_directory)
                # Create the record.
                rc.create_record(name=name, output_directory=output_directory, immovable=immovable)
                # Upload the asset bundles and add the record.
                lib = AssetBundles.upload_asset_bundles(name=name,
                                                        asset_bundles_directory=str(output_directory.resolve()),
                                                        librarian=lib,
                                                        record=RobotRecord(loads(output_directory.joinpath("record.json").read_text())),
                                                        url_infix="robots",
                                                        write=True,
                                                        quiet=False)
            # Create a new prefab.
            else:
                # Get parameter values from the dictionary or use default values.
                if "up" in robot:
                    up: str = robot["up"]
                else:
                    up: str = "y"
                if "xacro_args" in robot:
                    xacro_args = robot["xacro_args"]
                else:
                    xacro_args = None
                if "required_repo_urls" in robot:
                    required_repo_urls = robot["required_repo_urls"]
                else:
                    required_repo_urls = None
                rc.source_url_to_asset_bundles(url=url, output_directory=output_directory,
                                               required_repo_urls=required_repo_urls,
                                               xacro_args=xacro_args,
                                               immovable=immovable, description_infix=description_infix,
                                               branch=branch)
