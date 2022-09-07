from tdw.asset_bundle_creator.humanoid_creator_base import HumanoidCreatorBase


class AnimationCreator(HumanoidCreatorBase):
    """
    Create animation asset bundles from .anim or .fbx files.
    """

    def get_creator_class_name(self) -> str:
        return "AnimationCreator"
