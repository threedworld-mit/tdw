from tdw.controller import Controller
from tdw.librarian import ModelRecord
from typing import Tuple, List
from tdw.output_data import LogMessage
from tdw.backend import paths
from subprocess import Popen
import json
from pathlib import Path
from argparse import ArgumentParser
from tdw.model_pipeline.missing_materials import MissingMaterials


class Validator(Controller):
    """
    Check a model asset bundle for problems.
    First, load the model into the build and report back any errors.
    Then, scan the model for missing materials.

    This controller will attempt to launch a build.
    If one doesn't exist at the expected location, you'll need to launch one manually.
    """

    PINK_MATERIALS_REPORT: List[str] = ["This model has missing (pink) materials."]

    def __init__(self, record_path: str, asset_bundle_path: str, port=1071):
        """
        :param record_path: The path to the temporary record file.
        :param asset_bundle_path: The path to the local asset bundle.
        :param port: The port.
        """

        self.record_path: str = record_path
        self.record: ModelRecord = ModelRecord(json.loads(Path(record_path).read_text(encoding="utf-8")))
        self.asset_bundle_path: str = asset_bundle_path
        if not self.asset_bundle_path.startswith("file:///"):
            self.asset_bundle_path = "file:///" + self.asset_bundle_path

        super().__init__(port)

    def run(self, quiet=True) -> Tuple[bool, List[str]]:
        """
        Run verification. First, test for general errors with the model. Next, test for missing materials.

        :param quiet: If true, suppress messages.
        """

        MissingMaterials.start(self)

        # Run the verifier.
        if not quiet:
            print("Running verifier...")

        resp = self.communicate({"$type": "send_model_report",
                                 "name": self.record.name,
                                 "url": self.asset_bundle_path,
                                 "id": self.get_unique_id(),
                                 "scale_factor": self.record.scale_factor})
        reports = []
        for r in resp[:-1]:
            msg = LogMessage(r)
            reports.append(msg.get_message_type() + ": " + msg.get_message())

        # Check for missing materials.
        if not quiet:
            print("Checking for missing materials...")

        pink_materials = MissingMaterials.materials_are_missing(self, self.record, self.asset_bundle_path)
        if pink_materials:
            reports.append(self.PINK_MATERIALS_REPORT)

        self.kill_build()
        return len(reports) == 0, reports

    def kill_build(self):
        """
        Kill the build process.
        """

        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--record_path", type=str, help="The path to the temporary record file.")
    parser.add_argument("--asset_bundle_path", type=str, help="The path to the local asset bundle.")
    args = parser.parse_args()

    # Get the physics quality.
    c = Validator(record_path=args.record_path,
                  asset_bundle_path=args.asset_bundle_path)
    ok, reports = c.run()
    report = {"ok": ok,
              "reports": reports}

    root_dir = paths.ASSET_BUNDLE_VERIFIER_OUTPUT_DIR
    if not root_dir.exists():
        root_dir.mkdir(parents=True)
    paths.VALIDATOR_REPORT_PATH.write_text(json.dumps(report), encoding="utf-8")
