from tdw.controller import Controller
from tdw.output_data import VRRig, OutputData


class VR(Controller):
    """
    1. Create an Oculus VR rig.
    2. Add a few objects to the scene that can be picked up, moved, put down, etc.
    """

    def run(self):
        # Load the streamed scene and add controller rig.
        self.load_streamed_scene(scene="tdw_room_2018")

        self.communicate({"$type": "create_vr_rig"})

        # Add the table object and make it kinematic.
        table_id = self.add_object("small_table_green_marble",
                                   position={"x": 0, "y": 0, "z": 0.5})
        self.communicate([{"$type": "set_kinematic_state",
                           "id": table_id,
                           "is_kinematic": True}])

        # Add a box object and make it graspable.
        graspable_id_box = self.add_object("woven_box",
                                           position={"x": 0.2, "y": 1.0, "z": 0.5},
                                           library="models_core.json")
        self.communicate([{"$type": "set_graspable",
                           "id": graspable_id_box}])

        # Add the ball object and make it graspable.
        graspable_id = self.add_object("prim_sphere",
                                       position={"x": 0.2, "y": 3.0, "z": 0.5},
                                       library="models_special.json")
        self.communicate([{"$type": "set_graspable",
                          "id": graspable_id},
                          {"$type": "scale_object",
                           "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2},
                           "id": graspable_id}])
        # Receive VR data.
        resp = self.communicate({"$type": "send_vr_rig",
                                 "frequency": "once"})
        assert len(resp) > 1 and OutputData.get_data_type_id(resp[0]) == "vrri"
        vr = VRRig(resp[0])
        print(vr.get_head_rotation())

        # Start an infinite loop to allow the build to simulate physics.
        while True:
            self.communicate({"$type": "do_nothing"})


if __name__ == "__main__":
    VR().run()
