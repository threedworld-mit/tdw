from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from time import sleep


"""
Adjust the render quality of visual materials.
"""


class VisualMaterialQuality(Controller):
    def run(self):
        # Parse the substructure of fridge_large.
        record = ModelLibrarian().get_record("fridge_large")

        self.start()
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Create the object.
        o_id = self.add_object("fridge_large")

        # Add an avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 1.886, "z": -0.15},
                                                look_at=TDWUtils.VECTOR3_ZERO))

        # Disable post-processing, so the changes to the material aren't blurry.
        self.communicate({"$type": "set_post_process",
                          "value": False})

        for quality in ["low", "med", "high"]:
            # Set the visual materials.
            self.communicate(TDWUtils.set_visual_material(self, record.substructure, o_id,
                                                          "parquet_long_horizontal_clean", quality=quality))

            sleep(5)
            self.communicate({"$type": "unload_asset_bundles",
                              "bundle_type": "materials"})
        self.communicate({"$type": "unload_asset_bundles",
                          "bundle_type": "models"})


VisualMaterialQuality().run()
