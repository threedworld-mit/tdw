from platform import system
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.backend.platforms import SYSTEM_TO_UNITY

"""
Create a local asset bundle and load it into TDW.

See `Documentation/misc_frontend/add_local_object.md` for how to run the Asset Bundle Creator.
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
                c.start()
                # Create the environment.
                # Add the object.
                commands = [{"$type": "create_empty_environment"},
                            {"$type": "add_object",
                             "name": "cube",
                             "url": url,
                             "scale_factor": 1,
                             "id": c.get_unique_id()}]
                # Create the avatar.
                commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 0, "z": -3.6}))
                c.communicate(commands)
                return


if __name__ == "__main__":
    LocalObject.run()
