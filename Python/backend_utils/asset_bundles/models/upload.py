from enum import Enum
from pathlib import Path
from sys import exit
from argparse import ArgumentParser
import json
from typing import Dict, Callable, Optional
from requests import get
from requests.exceptions import RequestException
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.platforms import SYSTEM_TO_S3
from tdw.dev.asset_bundles import AssetBundles


class Stage(Enum):
    """
    A stage in the model pipeline.
    """

    create_prefab = 0
    create_asset_bundles = 1
    create_record = 2
    upload_asset_bundles = 3
    push = 4


class ModelPipeline:
    def __init__(self, model_name: str, source_path: str, library: str = "models_full.json"):
        """
        :param model_name: The name of the model.
        :param source_path: The absolute path to the source file.
        :param library: The library that will be modified.
        """

        # Load the config data.
        config_path = Path.home().joinpath("tdw_config").joinpath("model_pipeline.ini").resolve()
        assert config_path.exists(), f"Config file not found: {config_path}\n" \
                                     f"See documentation for how to write a new config file."
        config_text = config_path.read_text(encoding="utf-8").split("\n")
        config_data: Dict[str, str] = dict()
        for line in config_text:
            line_split = line.split("=")
            config_data[line_split[0].strip().lower()] = line_split[1].strip().lower()
        self.output_directory: Path = Path(config_data["output_directory"]).joinpath(model_name).resolve()
        if "editor_path" in config_data:
            editor_path = config_data["editor_path"]
        else:
            editor_path = None
        self.librarian: ModelLibrarian = ModelLibrarian(library)
        self.model_name: str = model_name
        self.source_path: str = source_path
        self.asset_bundle_creator: ModelCreator = ModelCreator(unity_editor_path=editor_path)
        self.record: Optional[ModelRecord] = self.librarian.get_record(model_name)
        # The pipeline sequence.
        self.pipeline: Dict[Stage, Callable] = {Stage.create_prefab: self.create_prefab,
                                                Stage.create_asset_bundles: self.create_asset_bundles,
                                                Stage.create_record: self.create_record,
                                                Stage.upload_asset_bundles: self.upload_asset_bundles,
                                                Stage.push: self.push}
        # Set the bucket.
        if library == "models_full.json":
            self.bucket: str = "tdw-private"
        else:
            self.bucket = "tdw-public"
        self.url_prefix: str = f"https://{self.bucket}.s3.amazonaws.com/models"

    def run(self, start_key: str, end_key: str) -> None:
        """
        Run a segment of the pipeline.

        :param start_key: The name of the start stage.
        :param end_key: The name of the end stage.
        """

        start = Stage[start_key]
        end = Stage[end_key]
        started = False
        for stage in Stage:
            # Start doing stages.
            if stage == start:
                started = True
            # Do the stage.
            if started:
                self.pipeline[stage]()
            # End now.
            if stage == end:
                started = False

    def create_prefab(self) -> None:
        """
        Create a .prefab from the .fbx file and the .obj file.
        """

        self.asset_bundle_creator.source_file_to_prefab(name=self.model_name,
                                                        source_file=self.source_path,
                                                        output_directory=self.output_directory)

    def create_record(self) -> None:
        """
        Create a metadata record and add it to the record database.
        """

        # Assemble just the parts of the possible that we can do outside of Unity.
        if self.record:
            overwrite = True
            wnid = self.record.wnid
            wcategory = self.record.wcategory
        # Create a new record.
        else:
            overwrite = False
            # Get ImageNet data.
            imagenet_path = Path("imagenet_data.json")
            imagenet_data = json.loads(imagenet_path.read_text(encoding="utf-8"))
            # Type a category.
            wcategory = input("Type the category here: ").lower()
            wnid = ModelPipeline.get_wnid(wcategory, imagenet_data)
            while wnid is None:
                print("Invalid category name.")
                wcategory = input("Type the category here: ").lower()
                wnid = ModelPipeline.get_wnid(wcategory, imagenet_data)
        self.asset_bundle_creator.create_record(name=self.model_name, output_directory=self.output_directory,
                                                wnid=wnid, wcategory=wcategory, scale_factor=1)
        record_path = self.output_directory.joinpath("record.json")
        # Write physics quality.
        self.asset_bundle_creator.write_physics_quality(name=self.model_name, record_path=record_path)
        # Check for other problems.
        self.asset_bundle_creator.validate(name=self.model_name, record_path=record_path)
        # Load the record.
        record = ModelRecord(data=json.loads(record_path.read_text(encoding="utf-8")))
        # Set the URLs.
        record.urls = {s: f'{self.url_prefix}/{SYSTEM_TO_S3[s]}/{ModelCreator.UNITY_VERSION}/{self.model_name}'
                       for s in SYSTEM_TO_S3}
        # Create the record.
        self.librarian.add_or_update_record(record, overwrite=overwrite, write=True)
        # If we're writing to the core library, append this record to the full library too.
        if "models_core.json" in self.librarian.library:
            ModelLibrarian("models_full.json").add_or_update_record(record, overwrite=overwrite, write=True)
        print("Set the record.")

    def create_asset_bundles(self) -> None:
        """
        Given a .prefab, create asset bundles. Save them locally.
        """

        self.asset_bundle_creator.prefab_to_asset_bundles(name=self.model_name, output_directory=self.output_directory)

    def upload_asset_bundles(self) -> None:
        """
        Download existing asset bundles (if any) and upload new asset bundles.
        """

        # Download backups.
        asset_bundle_backup_directory = self.output_directory.joinpath("backups")
        # Create the backup directory.
        if not asset_bundle_backup_directory.exists():
            asset_bundle_backup_directory.mkdir(parents=True)
        if self.record is not None:
            for platform in self.record.urls:
                url = self.record.urls[platform]
                resp = None
                try:
                    resp = get(url)
                except RequestException:
                    print("Couldn't download: " + url)
                if resp.status_code != 200:
                    f"Got a {resp.status_code} error when trying to download: {url}"
                    continue
                asset_bundle_backup = asset_bundle_backup_directory.joinpath(platform)
                if not asset_bundle_backup.exists():
                    asset_bundle_backup.mkdir()
                asset_bundle_backup = asset_bundle_backup.joinpath(self.record.name)
                asset_bundle_backup.write_bytes(resp.content)
                print(f"Downloaded: {asset_bundle_backup}")
        print("Created a backup of all asset bundles.")
        # Upload new asset bundles.
        self.librarian = AssetBundles.upload_asset_bundles(name=self.model_name,
                                                           asset_bundles_directory=str(self.output_directory.resolve()),
                                                           librarian=self.librarian,
                                                           record=self.record,
                                                           bucket=self.bucket,
                                                           write=True,
                                                           quiet=False)

    def push(self) -> None:
        """
        Push changes to GitHub.
        """

        AssetBundles.git_push(message=f"Added: {self.model_name}")

    @staticmethod
    def get_wnid(category, imagenet_data) -> Optional[str]:
        """
        Returns the best synset ID associated with the category.

        :param category: The category.
        :param imagenet_data: The categories data structure.

        :return: The best WordNet ID, or None if there is no good option.
        """

        # Get all wnids that have the category word.
        wnids = []
        for wnid in imagenet_data:
            if category in imagenet_data[wnid]:
                wnids.append(wnid)
        # Check if this word is valid.
        if len(wnids) == 0:
            return None
        # Just use the first wnid.
        else:
            return wnids[0]


if __name__ == "__main__":
    choices = [stage.name for stage in Stage]
    parser = ArgumentParser()
    parser.add_argument("--name", type=str, help="The model name.")
    parser.add_argument("--source", type=str, help="The absolute path to the source file.")
    parser.add_argument("-s", required=True, help="Start stage", choices=choices)
    parser.add_argument("-e", required=True, help="End stage", choices=choices)
    parser.add_argument("--library", type=str, default="models_core.json",
                        choices=ModelLibrarian.get_library_filenames(),
                        help="Write the metadata to this library.")
    args = parser.parse_args()
    # The model name can't have upper-case letters.
    if args.name.lower() != args.name:
        print(args.model_name + " contains capital letters, which is not allowed.")
        exit()
    if " " in args.name:
        print("Model name cannot have spaces. Consider using_underscore_instead.")
        exit()
    m = ModelPipeline(args.name, args.source, args.library)
    m.run(args.s, args.e)
