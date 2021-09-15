from platform import system
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.controller import Controller
from tdw.backend.platforms import SYSTEM_TO_UNITY
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a local asset bundle and load it into TDW.
"""


class LocalObject:
    @staticmethod
    def run():
        # Create the asset bundle and the record.
        asset_bundle_paths, record_path = AssetBundleCreator().create_asset_bundle("cube.fbx", True, 123, "", 1)
        # Get the name of the bundle for this platform. For example, Windows -> "StandaloneWindows64"
        bundle = SYSTEM_TO_UNITY[system()]
        # Get the correct asset bundle path.
        for p in asset_bundle_paths:
            # Get the path to the asset bundle.
            if bundle in str(p.parent.resolve()):
                url = "file:///" + str(p.resolve())

                # Launch the controller.
                c = Controller()
                camera = ThirdPersonCamera(position={"x": 0, "y": 0, "z": -3.6}, avatar_id="a")
                images_path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
                print(f"Images will be saved to: {images_path}")
                capture = ImageCapture(avatar_ids=["a"], path=images_path)
                c.add_ons.extend([camera, capture])
                c.communicate([{"$type": "create_empty_environment"},
                               {"$type": "add_object",
                                "name": "cube",
                                "url": url,
                                "scale_factor": 1,
                                "id": c.get_unique_id()}])
                c.communicate({"$type": "terminate"})


if __name__ == "__main__":
    LocalObject.run()
