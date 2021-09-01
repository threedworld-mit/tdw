from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
Create a humanoid and play some animations.
"""


class HumanoidAnimation(Controller):
    def run(self):
        open_can_record = HumanoidAnimationLibrarian().get_record("walking_2")
        h_id = self.get_unique_id()
        t_id = self.get_unique_id()
        self.start()
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "add_humanoid",
                           "name": "ha_proto_v1a",
                           "position": {"x": 0, "y": 0, "z": -4},
                           "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//no_physics",
                           "id": h_id},
                         self.get_add_humanoid_animation(humanoid_animation_name=open_can_record.name)[0],
                           {"$type": "play_humanoid_animation",
                             "name": open_can_record.name,
                             "id": h_id}])

        self.communicate(TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3}))

        # Add the objects.
        self.communicate([self.get_add_object(model_name="live_edge_coffee_table",
                                             object_id=9999,
                                             position={"x": 0, "y": 0, "z": 0},
                                             rotation={"x": 0, "y": 0, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="chair_billiani_doll",
                                             object_id=5555,
                                             position={"x": -0.3, "y": 0, "z": -2},
                                             rotation={"x": 0, "y": 63.25, "z": 0},
                                             library="models_core.json"),
                          self.get_add_object(model_name="zenblocks",
                                             object_id=t_id,
                                             position={"x": 0, "y": 1, "z": 0},
                                             rotation={"x": 0, "y": 90, "z": 0},
                                             library="models_core.json")])

        self.communicate({"$type": "set_ik_graspable", "id": t_id})

        # Make Unity's framerate match that of the animation clip.
        self.communicate({"$type": "set_target_framerate", "framerate": open_can_record.framerate})

        frame = 0
        num_frames = open_can_record.get_num_frames()
        while frame < num_frames:
            self.communicate([])
            frame += 1
     
        self.communicate({"$type": "humanoid_reach_for_target", "target": t_id, "id": h_id, "arm": "right"})

        for i in range(100):
            self.communicate([])		

if __name__ == "__main__":
    HumanoidAnimation(launch_build=False).run()
