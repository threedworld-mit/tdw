from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.output_data import OutputData, Transforms
from random import uniform
import os
import numpy as np


"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""


class HumanoidAnimation(Controller):
    def run(self):
        walk_record = HumanoidAnimationLibrarian().get_record("walking_2")

        h_id = self.get_unique_id()
        t_id = self.get_unique_id()

        # Make Unity's framerate match that of the animation clip.
        self.communicate({"$type": "set_target_framerate", "framerate": walk_record.framerate})

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                         self.get_add_object(model_name="live_edge_coffee_table",
                                             object_id=9999,
                                             position={"x": 0, "y": 0, "z": 0},
                                             rotation={"x": 0, "y": 0, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="chair_billiani_doll",
                                             object_id=5555,
                                             position={"x": -0.3, "y": 0, "z": -2},
                                             rotation={"x": 0, "y": 63.25, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="chair_billiani_doll",
                                             object_id=6666,
                                             position={"x": 0.3, "y": 0, "z": -2},
                                             rotation={"x": 0, "y": 63.25, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="golf",
                                             object_id=t_id,
                                             position={"x": 0, "y": 1, "z": 0},
                                             rotation={"x": 0, "y": 90, "z": 0},
                                             library="models_core.json"),
                          {"$type": "set_kinematic_state", "id": t_id, "is_kinematic": True, "use_gravity": False},
                          {"$type": "set_ik_graspable", "id": t_id},
                          {"$type": "add_humanoid",
                           "name": "ha_proto_v1a",
                           "position": {"x": 0, "y": 0, "z": -4},
                           "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                           "id": h_id},
                         self.get_add_humanoid_animation(humanoid_animation_name=walk_record.name)[0],
                           {"$type": "play_humanoid_animation",
                             "name": walk_record.name,
                             "id": h_id},
                          {"$type": "send_humanoids",
                           "ids": [h_id],
                           "frequency": "always"},
                          {"$type": "send_transforms",
                           "ids": [t_id],
                           "frequency": "always"}])

        self.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3}))
        if walk_record.loop:
            num_loops = 4
        frame = 0
        num_frames = walk_record.get_num_frames()
        print("Number of frames = " + str(num_frames))
        while frame < num_frames:
            self.communicate([])
            frame += 1

if __name__ == "__main__":
    HumanoidAnimation(launch_build=False).run()
