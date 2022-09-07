from tdw.asset_bundle_creator.humanoid_creator_base import HumanoidCreatorBase


class HumanoidCreator(HumanoidCreatorBase):
    """
    Create asset bundles of non-physics humanoids from .fbx files.
    """

    def get_creator_class_name(self) -> str:
        return "HumanoidCreator"
