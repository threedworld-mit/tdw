from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.output_data import OutputData, Transforms
from random import uniform
from time import sleep
import os
from math import ceil
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
        chair_id = self.get_unique_id()
        teak_id = self.get_unique_id()
        meters_per_frame = 0.04911
        chair_pos = {"x": 1.25, "y": 0, "z": -2}
        teak_pos = {"x": -3.25, "y": 0, "z": -2}

        om = ObjectManager()
        self.add_ons.append(om)

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
                                             object_id=chair_id,
                                             position=chair_pos,
                                             rotation={"x": 0, "y": 0, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="chista_slice_of_teak_table",
                                             object_id=teak_id,
                                             position=teak_pos,
                                             rotation={"x": 0, "y": 0, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="golf",
                                             object_id=t_id,
                                             position={"x": 0, "y": 1, "z": 0},
                                             rotation={"x": 0, "y": 90, "z": 0},
                                             library="models_core.json"),
                          {"$type": "set_kinematic_state", "id": t_id, "is_kinematic": True, "use_gravity": False},
                          {"$type": "add_humanoid",
                           "name": "ha_proto_v1a",
                           "position": {"x": 0, "y": 0, "z": -4},
                           "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                           "id": h_id},
                         self.get_add_humanoid_animation(humanoid_animation_name=walk_record.name)[0],
                          {"$type": "send_humanoids",
                           "ids": [h_id],
                           "frequency": "always"},
                          {"$type": "send_transforms",
                           "ids": [chair_id],
                           "frequency": "always"}])
        self.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3}))
        # Walk to table initially
        self.communicate({"$type": "play_humanoid_animation",
                          "name": walk_record.name,
                          "id": h_id})
        if walk_record.loop:
            num_loops = 4
        frame = 0
        num_frames = walk_record.get_num_frames()
        while frame < num_frames:
            self.communicate([])
            frame += 1
        sleep(2)
        # Turn to face chair.
        self.communicate({"$type": "humanoid_look_at", 
                               "other_object_id": chair_id, 
                               "id": h_id})
        sleep(2)
        distance = TDWUtils.get_distance(TDWUtils.array_to_vector3(om.transforms[h_id].position), chair_pos) 
        # Walk towards the chair.
        self.communicate({"$type": "play_humanoid_animation",
                          "name": walk_record.name,
                          "id": h_id})
        if walk_record.loop:
            num_loops = 4
        frame = 0
        num_frames = int(distance / meters_per_frame)
        while frame < num_frames:
            self.communicate([])
            frame += 1
        # Turn to face teak table.
        self.communicate({"$type": "humanoid_look_at", 
                               "other_object_id": teak_id, 
                               "id": h_id})
        sleep(2)
        distance2 = TDWUtils.get_distance(TDWUtils.array_to_vector3(om.transforms[h_id].position), teak_pos) 
        # Walk towards the chair.
        num_frames = int(distance2 / meters_per_frame)
        if num_frames <= walk_record.get_num_frames():
            self.communicate({"$type": "play_humanoid_animation",
                              "name": walk_record.name,
                              "id": h_id})
            frame = 0
            while frame < num_frames:
                self.communicate([])
                frame += 1
        else:
            num_loops = int(num_frames / walk_record.get_num_frames())
            for i in range(num_loops):
                self.communicate([])
                self.communicate({"$type": "play_humanoid_animation",
                                  "name": walk_record.name,
                                  "id": h_id})
                frame = 0
                while frame < walk_record.get_num_frames():
                    self.communicate([])
                    frame += 1
            remainder = num_frames - (walk_record.get_num_frames() * num_loops)
            self.communicate({"$type": "play_humanoid_animation",
                              "name": walk_record.name,
                              "id": h_id})
            frame = 0
            while frame < remainder:
                self.communicate([])
                frame += 1

    #def walk_to_object(self, object_id):
        
if __name__ == "__main__":
    HumanoidAnimation(launch_build=False).run()
