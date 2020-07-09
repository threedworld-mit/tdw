from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import CompositeObjects


"""
Create a box with a lid and a Sticky Mitten Avatar.
Tell the Sticky Mitten Avatar to open the box.
"""


class OpenBox(Controller):
    def run(self):
        self.start()
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Add the box.
        o_id = self.add_object("rattan_basket",
                               position={"x": 1.327, "y": 0, "z": 3.174},
                               rotation={"x": 0, "y": -50, "z": 0})

        self.communicate({"$type": "set_mass",
                          "id": o_id,
                          "mass": 1000})

        # Get the ID of the lid sub-object.
        resp = self.communicate({"$type": "send_composite_objects"})
        comp = CompositeObjects(resp[0])
        lid_id = None
        for s in range(comp.get_num_sub_objects(0)):
            sub_object_type = comp.get_sub_object_machine_type(0, s)
            sub_object_id = comp.get_sub_object_id(0, s)
            if sub_object_type == "hinge":
                lid_id = sub_object_id

        self.communicate(TDWUtils.create_avatar(avatar_type="A_StickyMitten_Adult"))

        self.communicate({"$type": "set_avatar_drag",
                          "angular_drag": 5,
                          "drag": 80})

        # Go to the fridge.
        for i in range(200):
            self.communicate([{"$type": "move_avatar_forward_by",
                               "magnitude": 300},
                              {"$type": "turn_avatar_by",
                               "torque": 10}])
        for i in range(50):
            self.communicate({"$type": "move_avatar_forward_by",
                              "magnitude": 300})

        # Bend the arm joints.
        self.communicate([{"$type": "set_avatar_drag",
                           "angular_drag": 1000,
                           "drag": 1000},
                          {"$type": "bend_arm_joint_by",
                           "joint": "shoulder_right",
                           "axis": "pitch",
                           "angle": 43},
                          {"$type": "bend_arm_joint_by",
                           "joint": "shoulder_right",
                           "axis": "yaw",
                           "angle": 10},
                          {"$type": "bend_arm_joint_by",
                           "joint": "shoulder_right",
                           "axis": "roll",
                           "angle": -5},
                          {"$type": "bend_arm_joint_by",
                           "joint": "elbow_right",
                           "axis": "pitch",
                           "angle": 30},
                          {"$type": "bend_arm_joint_by",
                           "joint": "wrist_right",
                           "axis": "pitch",
                           "angle": 20}])
        for i in range(100):
            self.communicate({"$type": "do_nothing"})

        # Scoot a little more forward.
        self.communicate({"$type": "set_avatar_drag",
                          "angular_drag": 5,
                          "drag": 80})
        for i in range(65):
            self.communicate({"$type": "move_avatar_forward_by",
                              "magnitude": 300})

        # Place the mitt on the lid.
        self.communicate([{"$type": "set_avatar_drag",
                           "angular_drag": 1000,
                           "drag": 1000},
                          {"$type": "bend_arm_joint_to",
                           "joint": "shoulder_right",
                           "axis": "pitch",
                           "angle": 10},
                          {"$type": "bend_arm_joint_to",
                           "joint": "wrist_right",
                           "axis": "pitch",
                           "angle": 0}])

        for i in range(100):
            self.communicate({"$type": "do_nothing"})

        # "Pick up" the lid.
        self.communicate([{"$type": "set_stickiness",
                           "sub_mitten": "palm",
                           "sticky": True,
                           "is_left": False},
                          {"$type": "pick_up_proximity",
                           "grip": 2000,
                           "is_left": False,
                           "object_ids": [lid_id]},
                          {"$type": "bend_arm_joint_by",
                           "joint": "shoulder_right",
                           "axis": "pitch",
                           "angle": -10},
                          {"$type": "bend_arm_joint_by",
                           "joint": "elbow_right",
                           "axis": "pitch",
                           "angle": 70},
                          {"$type": "bend_arm_joint_by",
                           "joint": "wrist_right",
                           "axis": "pitch",
                           "angle": 35}])
        for i in range(100):
            self.communicate({"$type": "do_nothing"})


if __name__ == "__main__":
    OpenBox().run()
