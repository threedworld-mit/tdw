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
        open_can_record = HumanoidAnimationLibrarian().get_record("walking_2")

        h_id = self.get_unique_id()
        t_id = self.get_unique_id()
        self.start()

        # Make Unity's framerate match that of the animation clip.
        self.communicate({"$type": "set_target_framerate", "framerate": open_can_record.framerate})

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
                           "url": "file:///" + "D://no_ik",
                           "id": h_id},
                         self.get_add_humanoid_animation(humanoid_animation_name=open_can_record.name)[0],
                           {"$type": "play_humanoid_animation",
                             "name": open_can_record.name,
                             "id": h_id},
                          {"$type": "send_humanoids",
                           "ids": [h_id],
                           "frequency": "always"},
                          {"$type": "send_transforms",
                           "ids": [t_id],
                           "frequency": "always"}])

        self.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3}))

        frame = 0
        num_frames = open_can_record.get_num_frames()
        while frame < num_frames:
            self.communicate([])
            frame += 1

        for i in range(20):
            resp = self.communicate({"$type": "teleport_object", "position": {"x": uniform(-0.5, 0.5), "y": uniform(0.4, 1.75), "z": uniform(-0.1, 0.2)}, "id": t_id})
            for r in resp[:-1]:
                r_id = OutputData.get_data_type_id(r)
                # Find the transform data.
                if r_id == "tran":
                    t = Transforms(r)
                    if t.get_id(0) == h_id:
                        ha_forward = np.array(t.get_forward(0))
                        ha_position = np.array(t.get_position(0))
                    if t.get_id(0) == t_id:
                        tgt_position = np.array(t.get_position(0))

            pos_val = self.get_direction(ha_forward, ha_position, tgt_position)

            if pos_val < 0:
                self.reach_for_target(arm="left", humanoid=h_id, target=t_id, reach_action_length=20, reset_action_length=30)
            else:
                self.reach_for_target(arm="right", humanoid=h_id, target=t_id, reach_action_length=20, reset_action_length=30)

    
    def reach_for_target(self, arm: str, humanoid: int, target: int, reach_action_length: int, reset_action_length: int):
        self.communicate({"$type": "humanoid_reach_for_target", "target": target, "id": humanoid, "length": reach_action_length, "arm": arm})
        frame = 0
        while frame < reach_action_length:
            self.communicate([])
            frame += 1

        self.communicate({"$type": "humanoid_reset_arm", "id": humanoid, "length": reset_action_length, "arm": arm})

        frame = 0
        while frame < reset_action_length:
            self.communicate([])
            frame += 1


    def get_direction(self, forward: np.array, origin: np.array, target: np.array) -> bool:
        """
        :param forward: The forward directional vector.
        :param origin: The origin position.
        :param target: The target position.

        :return: True if the target is to the left of the origin by the forward vector; False if it's to the right.
        """
        # Get the heading.
        target_direction = target - origin
        # Normalize the heading.
        #target_direction = target_direction / np.linalg.norm(target_direction)
        perpendicular: np.array = np.cross(forward, target_direction)
        direction = np.dot(perpendicular, QuaternionUtils.UP)
        return direction


if __name__ == "__main__":
    HumanoidAnimation(launch_build=False).run()