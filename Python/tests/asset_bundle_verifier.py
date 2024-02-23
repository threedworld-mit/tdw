from time import sleep, time
from tdw.output_data import LogMessage
from tdw.librarian import ModelLibrarian, MaterialLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tqdm import tqdm
from argparse import ArgumentParser
from typing import List, Dict
from tdw.backend.paths import ASSET_BUNDLE_VERIFIER_OUTPUT_DIR
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from platform import system


class _AssetBundleVerifier(Controller):
    """
    Verify that each asset bundle in a collection doesn't have errors.
    """

    def run(self, resume: bool):
        # User must have valid credentials for tdw-private.
        if not TDWUtils.validate_amazon_s3():
            return
        lib = self._get_librarian()
        report: Dict[str, List[str]] = {}
        # Get an existing report.
        processed: List[str] = []
        output_path = ASSET_BUNDLE_VERIFIER_OUTPUT_DIR
        if not output_path.exists():
            output_path.mkdir()
        filename = Path(lib.library).name
        output_path = output_path.joinpath(filename)
        if output_path.exists():
            if resume:
                report = json.loads(output_path.read_text(encoding="utf-8"))
                for key in report:
                    processed.append(key)
            else:
                output_path.unlink()

        # Get a list of keys of tdw-private objects.
        session = boto3.Session(profile_name="tdw")
        s3 = session.resource("s3")
        self.communicate([{"$type": "simulate_physics", "value": False},
                          {"$type": "create_empty_environment"}])
        pbar = tqdm(total=len(lib.records))
        for record in lib.records:
            if not self._process_record(record) or record.name in processed:
                pbar.update(1)
                continue
            pbar.set_description(record.name)
            # Check the URLs.
            urls_exist = True
            for url in record.urls.values():
                if "tdw-private" in url:
                    bucket = "tdw-private"
                    key = url.replace("https://tdw-private.s3.amazonaws.com/", "")
                else:
                    bucket = "tdw-public"
                    key = url.replace("https://tdw-public.s3.amazonaws.com/", "")
                try:
                    s3.meta.client.head_object(Bucket=bucket, Key=key)
                except ClientError:
                    if record.name not in report:
                        report[record.name] = list()
                    report[record.name].append("error: Asset bundle doesn't exist: " + url)
                    urls_exist = False
                # This happens if S3 refuses the connection due to too many queries.
                except EndpointConnectionError:
                    sleep(20)
            if not urls_exist:
                processed.append(record.name)
                pbar.update(1)
                continue
            # Create a new entry in the report.
            report[record.name] = list()
            # Load the asset bundle in the build.
            t0 = time()
            resp = self.communicate(self._get_process_commands(record))
            for r in resp[:-1]:
                msg = LogMessage(r)
                report[record.name].append(msg.get_message_type() + ": " + msg.get_message())
            # Write the report to disk.
            output_path.write_text(json.dumps(report, indent=4, sort_keys=True), encoding="utf-8")
            # Sleep to prevent the connection from being refused
            if time() - t0 < 1 and system() == "Linux":
                sleep(5)
            pbar.update(1)
        pbar.close()

        print("Done!")
        print("Output file: " + str(output_path.resolve()))
        print("")
        for name in report:
            if len(report[name]) > 0:
                print(name)
                for problem in report[name]:
                    print("\t" + problem)
        self.communicate({"$type": "terminate"})

    def _get_librarian(self):
        """
        Returns the Librarian object.
        """

        raise Exception()

    def _process_record(self, record) -> bool:
        """
        Returns true if this record should be processed.

        :param record: The record.
        """

        raise Exception()

    def _get_process_commands(self, sendable: str) -> dict:
        """
        Get the command used to process the record.

        :param sendable: The serialized record.
        """

        raise Exception()


class ModelAssetBundleVerifier(_AssetBundleVerifier):
    """
    Verify each model for this OS.
    """

    def _get_librarian(self):
        lib = ModelLibrarian("models_full.json")

        # Add the special models.
        special = ModelLibrarian("models_special.json")
        for record in special.records:
            lib.add_or_update_record(record, False, write=False)
        return lib

    def _process_record(self, record) -> bool:
        return not record.do_not_use

    def _get_process_commands(self, record) -> List[dict]:
        return [{"$type": "send_model_report",
                 "name": record.name,
                 "url": record.get_url(),
                 "id": self.get_unique_id(),
                 "scale_factor": record.scale_factor,
                 "flex": record.flex and system() != "Darwin"}]


class MaterialAssetBundleVerifier(_AssetBundleVerifier):
    """
    Verify each material asset bundle at each quality level for this OS.
    """

    def __init__(self, library: str):
        self.library = library
        super().__init__(launch_build=False)

    def _get_librarian(self):
        return MaterialLibrarian(self.library)

    def _process_record(self, record) -> bool:
        return True

    def _get_process_commands(self, record) -> List[dict]:
        return [{"$type": "send_material_report",
                 "name": record.name,
                 "url": record.get_url()}]


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--type", default="models", choices=["models", "materials"], help="The type of collection.")
    parser.add_argument("--resume", action="store_true", help="Continue a previous test.")
    args = parser.parse_args()

    if args.type == "models":
        ModelAssetBundleVerifier().run(args.resume)
    else:
        for library in MaterialLibrarian.get_library_filenames():
            print(library)
            MaterialAssetBundleVerifier(library).run(args.resume)
