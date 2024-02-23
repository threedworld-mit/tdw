from tdw.controller import Controller
from tdw.output_data import IdPassSegmentationColors


class IdPassSegmentationColorsTest(Controller):
    def run(self):
        # Initialize the scene.
        resp = self.communicate([{"$type": "create_empty_environment"},
                                 {"$type": "simulate_physics",
                                  "value": False},
                                 self.get_add_object("iron_box", object_id=0),
                                 self.get_add_object("iron_box", object_id=1, position={"x": 0, "y": 0.5, "z": 0}),
                                 {"$type": "create_avatar",
                                  "type": "A_Img_Caps_Kinematic",
                                  "id": "a"},
                                 {"$type": "teleport_avatar_to",
                                  "avatar_id": "a",
                                  "position": {"x": 0, "y": 0.5, "z": -1.3}},
                                 {"$type": "set_pass_masks",
                                  "avatar_id": "a",
                                  "pass_masks": ["_id"]},
                                 {"$type": "send_id_pass_segmentation_colors"}])
        i = IdPassSegmentationColors(resp[0])
        print(i.get_avatar_id())
        print(i.get_num_segmentation_colors())
        print(i.get_segmentation_color(0))
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    IdPassSegmentationColorsTest().run()
