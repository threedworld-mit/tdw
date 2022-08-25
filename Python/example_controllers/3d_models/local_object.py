from platform import system
from pathlib import Path
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a local asset bundle and load it into TDW.
"""

# Create the asset bundle and the record.
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
print(f"Images and asset bundles will be saved to: {output_directory}")
name = "cube"
AssetBundleCreator().source_file_to_asset_bundles(name=name,
                                                  source_file=Path("cube.fbx").resolve(),
                                                  output_directory=output_directory)
# Get the path to the asset bundle.
asset_bundle_path = output_directory.joinpath(system()).joinpath(name)
uri = f"file:///{str(asset_bundle_path.resolve())}"
# Launch the controller.
c = Controller()
camera = ThirdPersonCamera(position={"x": 0, "y": 0, "z": -3.6}, avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=output_directory)
c.add_ons.extend([camera, capture])
c.communicate([{"$type": "create_empty_environment"},
               {"$type": "add_object",
                "name": "cube",
                "url": uri,
                "scale_factor": 1,
                "id": c.get_unique_id()}])
c.communicate({"$type": "terminate"})
