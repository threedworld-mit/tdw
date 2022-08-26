from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from typing import List, Dict, NamedTuple, Union
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian, HumanoidAnimationRecord

class AnimationManager():

    # A dictionary of animation data per animation name.
    ANIMATION_DATA_LIST: Dict[str, HumanoidAnimationRecord] = dict()

    def __init__(self, animation_list: List[str]):
        self.animation_list = animation_list
        self.lib = HumanoidAnimationLibrarian()
        self.current_animation_record: HumanoidAnimationRecord

    def download_animations(self) -> List[dict]:
        # Prepare to download all of the animations in the list, caching the data for each one.
        commands = []
        for anim_name in self.animation_list:
            self.current_animation_record = self.lib.get_record(anim_name)
            AnimationManager.ANIMATION_DATA_LIST[anim_name] = self.current_animation_record
            anim_url = self.current_animation_record.get_url()
            commands.append({"$type": "add_humanoid_animation", 
                            "name": anim_name, 
                            "url": anim_url})
        return commands