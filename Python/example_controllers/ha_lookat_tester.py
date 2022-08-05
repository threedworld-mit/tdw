from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.controller import Controller
from typing import List, Dict, Union
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.output_data import OutputData, Transforms, LocalTransforms
from tdw.output_data import OutputData, EmptyObjects, Bounds
from random import uniform
from time import sleep
import os
import numpy as np


"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""


class ReachForAffordancePoint(Controller):

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.h_id = self.get_unique_id()
      

    def init_scene(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend([self.get_add_object(model_name="live_edge_coffee_table",
                                             object_id=9999,
                                             position={"x": 0, "y": 0, "z": 0},
                                             rotation={"x": 0, "y": 20, "z": 0},
                                             library="models_core.json"),
                         self.get_add_object(model_name="chair_billiani_doll",
                                             object_id=5555,
                                             position={"x": -0.3, "y": 0, "z": -2},
                                             rotation={"x": 0, "y": 63.25, "z": 0},
                                             library="models_core.json"),
                          {"$type": "set_kinematic_state", "id": 9999, "is_kinematic": True, "use_gravity": False},
                          {"$type": "add_humanoid",
                           "name": "ha_proto_v1a",
                           "position": {"x": 0, "y": 0, "z": -0.525},
                           "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                           #"url": "file:///" + "D://HumanoidAgent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                           "id": self.h_id},
                          {"$type": "send_humanoids",
                           "ids": [self.h_id],
                           "frequency": "always"}])
        self.communicate(commands)

    def run(self):
        walk_record = HumanoidAnimationLibrarian().get_record("walking_2")

        # Make Unity's framerate match that of the animation clip.
        self.communicate({"$type": "set_target_framerate", "framerate": walk_record.framerate})

        self.init_scene()

        self.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3}))

        resp = self.communicate([])

        for i in range(10):
            # Turn to face random positions.     
            self.communicate({"$type": "humanoid_look_at_position", 
                               "position": {"x": uniform(-5, 5), "y": 0, "z": uniform(-5, 5)}, 
                               "id": self.h_id})
            sleep(2)
        self.communicate({"$type": "humanoid_look_at", 
                               "other_object_id": 9999, 
                               "id": self.h_id})
        sleep(2)
        self.communicate({"$type": "humanoid_look_at", 
                               "other_object_id": 5555, 
                               "id": self.h_id})
if __name__ == "__main__":
    ReachForAffordancePoint(launch_build=False).run()
