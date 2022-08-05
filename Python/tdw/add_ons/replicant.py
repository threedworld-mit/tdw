from typing import List, Union, Dict
from pathlib import Path
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.add_ons.object_manager import ObjectManager
from tdw.output_data import OutputData, Transforms
from random import uniform
from time import sleep
import os
from math import ceil
import numpy as np

class Replicant(AddOn):

    def __init__(self):
        """
        :param path: The path to the output directory.

        """

        super().__init__()
        self.walk_record = HumanoidAnimationLibrarian().get_record("walking_2")
        self.meters_per_frame = 0.04911
        self.h_id = self.get_unique_id()

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "set_target_framerate", "framerate": self.walk_record.framerate},
                    {"$type": "add_humanoid",
                      "name": "ha_proto_v1a",
                       "position": {"x": 0, "y": 0, "z": -4},
                       "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                        "id": h_id},
                    self.get_add_humanoid_animation(humanoid_animation_name=self.walk_record.name)[0],
                    {"$type": "send_humanoids",
                           "ids": [self.h_id],
                           "frequency": "always"},
                    {"$type": "send_transforms",
                           "frequency": "always"}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        