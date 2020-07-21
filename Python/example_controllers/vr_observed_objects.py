from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, VRRig, IdPassSegmentationColors, SegmentationColors


"""
Create a VR rig and gather observed object data by attaching an avatar and using IdPassSegmentationColors output data.
"""


class VRObservedObjects(Controller):
    def run(self):
        self.start()
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Create the objects.
        statue_id = self.add_object("satiro_sculpture",
                                    position={"x": 2, "y": 0, "z": 1})
        # Request segmentation colors.
        resp = self.communicate({"$type": "send_segmentation_colors"})
        segmentation_colors = SegmentationColors(resp[0])

        # Get the segmentation color of the sculpture.
        statue_color = None
        for i in range(segmentation_colors.get_num()):
            if segmentation_colors.get_object_id(i) == statue_id:
                statue_color = segmentation_colors.get_object_color(i)
                break

        # Create the VR Rig.
        self.communicate({"$type": "create_vr_rig"})
        # Attach an avatar to the VR rig.
        self.communicate({"$type": "attach_avatar_to_vr_rig",
                          "id": "a"})
        # Request the colors of objects currently observed by the avatar per frame.
        # Request VR rig data per frame.
        # Reduce render quality in order to improve framerate.
        self.communicate([{"$type": "send_id_pass_segmentation_colors",
                           "frequency": "always"},
                          {"$type": "send_vr_rig",
                           "frequency": "always"},
                          {"$type": "set_post_process",
                           "value": False},
                          {"$type": "set_render_quality",
                           "render_quality": 0}])

        while True:
            resp = self.communicate({"$type": "do_nothing"})
            head_rotation = None
            can_see_statue = False
            for r in resp[:-1]:
                r_id = OutputData.get_data_type_id(r)
                # Get the head rotation.
                if r_id == "vrri":
                    head_rotation = VRRig(r).get_head_rotation()
                # Check if we can see the statue.
                elif r_id == "ipsc":
                    observed_objects = IdPassSegmentationColors(r)
                    for i in range(observed_objects.get_num_segmentation_colors()):
                        if observed_objects.get_segmentation_color(i) == statue_color:
                            can_see_statue = True
            if can_see_statue:
                print("You can see the object!\nHead rotation: " + str(head_rotation) + "\n")


if __name__ == "__main__":
    VRObservedObjects().run()
