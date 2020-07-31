from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

"""
- Add a StickyMittenAvatar to the scene.
- Add an object to the scene.
- Tell the avatar to pick up the object.
"""


class StickyMittenAvatar(Controller):
    def run(self):
        self.start()
        self.communicate(TDWUtils.create_empty_room(20, 20))

        # Add the avatar and the object.
        self.communicate(TDWUtils.create_avatar(avatar_type="A_StickyMitten_Adult"))
        o_id = self.add_object("jug05",
                               position={"x": -0.417, "y": 0.197, "z": 0.139},
                               rotation={"x": 90, "y": 0, "z": 0},
                               library="models_core.json")

        # 1. Disable the SensorContainer to ensure that the FollowCamera will render to the screen.
        # 2. Scale the object to be more visible.
        # 3. Set the back of the left mitten as "sticky".
        # 4. Set a high angular drag for the avatar to ensure that it won't spin like a top.
        # 5. Rotate the head to look down at the object.
        # 6. Pick up the object. Set a high grip to ensure that the avatar won't drop the object.
        # 7. Bend the arm joints.
        #
        # NOTE: We don't specify avatar_id because the default is "a",
        #       which is what TDWUtils.create_avatar sets it to.
        self.communicate([{"$type": "toggle_image_sensor",
                           "sensor_name": "SensorContainer"},
                          {"$type": "scale_object",
                           "scale_factor": {"x": 2.5, "y": 2.5, "z": 2.5},
                           "id": o_id},
                          {"$type": "set_stickiness",
                           "sub_mitten": "back",
                           "sticky": True,
                           "is_left": True},
                          {"$type": "set_avatar_drag",
                           "drag": 0.125,
                           "angular_drag": 1000},
                          {"$type": "rotate_head_by",
                           "axis": "pitch",
                           "angle": 25},
                          {"$type": "pick_up_proximity",
                           "distance": 20,
                           "grip": 10000,
                           "is_left": True},
                          {"$type": "bend_arm_joint_by",
                           "angle": 25,
                           "joint": "shoulder_left",
                           "axis": "pitch"},
                          {"$type": "bend_arm_joint_by",
                           "angle": -25,
                           "joint": "shoulder_left",
                           "axis": "yaw"},
                          {"$type": "bend_arm_joint_by",
                           "angle": 60,
                           "joint": "shoulder_left",
                           "axis": "roll"},
                          {"$type": "bend_arm_joint_by",
                           "angle": 100,
                           "joint": "elbow_left",
                           "axis": "pitch"},
                          {"$type": "bend_arm_joint_by",
                           "angle": 15,
                           "joint": "shoulder_right",
                           "axis": "pitch"},
                          {"$type": "bend_arm_joint_by",
                           "angle": -15,
                           "joint": "shoulder_right",
                           "axis": "yaw"},
                          {"$type": "bend_arm_joint_by",
                           "angle": 35,
                           "joint": "elbow_right",
                           "axis": "pitch"}])

        # Let the simulation run for a while to allow the arm joints to bend.
        for i in range(100):
            self.communicate([])
        # Move the avatar forward.
        for i in range(20):
            self.communicate({"$type": "move_avatar_forward_by",
                              "magnitude": 50})
        for i in range(100):
            self.communicate([])
        # Drop the object and bend the joints down.
        self.communicate([{"$type": "rotate_head_by",
                           "axis": "pitch",
                           "angle": 0},
                          {"$type": "put_down",
                           "is_left": True},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "shoulder_left",
                           "axis": "pitch"},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "shoulder_left",
                           "axis": "yaw"},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "shoulder_left",
                           "axis": "roll"},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "elbow_left",
                           "axis": "pitch"},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "shoulder_right",
                           "axis": "pitch"},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "shoulder_right",
                           "axis": "yaw"},
                          {"$type": "bend_arm_joint_to",
                           "angle": 0,
                           "joint": "elbow_right",
                           "axis": "pitch"}])
        for i in range(100):
            self.communicate([])


if __name__ == "__main__":
    StickyMittenAvatar().run()
