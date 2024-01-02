# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.command import Command


class UnloadAssetBundles(Command):
    """
    Unloads all AssetBundles. Send this command only after destroying all objects in the scene. This command should be used only to free up memory. After sending it, you will need to re-download any objects you want to add to a scene.
    """

    def __init__(self, bundle_type: str = "models"):
        """
        :param bundle_type: The type of asset bundle to unload from memory.
        """

        super().__init__()
        """:field
        The type of asset bundle to unload from memory.
        """
        self.bundle_type: str = bundle_type
