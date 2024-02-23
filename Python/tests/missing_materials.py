from tqdm import tqdm
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian
from tdw.add_ons.model_verifier.model_verifier import ModelVerifier
from tdw.backend.paths import ASSET_BUNDLE_VERIFIER_OUTPUT_DIR


class MissingMaterials(Controller):
    """
    Test each model in models_full.json for missing materials.
    """

    def run(self) -> None:
        if not ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.exists():
            ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.mkdir(parents=True)
        output_file = ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.joinpath("missing_materials.txt")
        # Create a new output file.
        if output_file.exists():
            output_file.unlink()
        print(f"Results will be saved to: {output_file}")
        lib = ModelLibrarian("models_full.json")
        records = [record for record in lib.records if not record.do_not_use]
        pbar = tqdm(total=len(records))
        verifier = ModelVerifier()
        self.add_ons.append(verifier)
        for record in records:
            pbar.set_description(record.name)
            verifier.set_tests(name=record.name, source=record, model_report=False, missing_materials=True,
                               physics_quality=False)
            while not verifier.done:
                self.communicate([])
            if len(verifier.reports) > 0:
                with output_file.open("at") as f:
                    f.write("\n" + record.name)
            pbar.update(1)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MissingMaterials()
    c.run()
