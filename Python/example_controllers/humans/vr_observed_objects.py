from typing import List, Dict
from json import dumps
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.output_data import OutputData, VRRig, IdPassSegmentationColors, SegmentationColors


class VRObservedObjects(Controller):
    """
    Add several objects to the scene. Record which objects are visible to the VR agent.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)
        self.segmentation_colors: Dict[tuple, str] = dict()
        self.frame_data: List[dict] = list()

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the table object and make it kinematic.
        commands.extend(self.get_add_physics_object(model_name="small_table_green_marble",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0, "y": 0, "z": 0.5},
                                                    kinematic=True,
                                                    library="models_core.json"))
        # Add a box object and make it graspable.
        box_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="woven_box",
                                                    object_id=box_id,
                                                    position={"x": 0.2, "y": 1.0, "z": 0.5},
                                                    library="models_core.json"))
        self.communicate([{"$type": "set_graspable",
                           "id": box_id}])
        # Add the ball object and make it graspable.
        sphere_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                                                    object_id=sphere_id,
                                                    position={"x": 0.2, "y": 3.0, "z": 0.5},
                                                    library="models_special.json",
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2}))
        commands.append({"$type": "set_graspable",
                         "id": sphere_id})
        # Receive VR data per frame.
        # Receive segmentation colors data only on this frame.
        # Reduce render quality in order to improve framerate.
        # Attach an avatar to the VR rig.
        # Request the colors of objects currently observed by the avatar per frame.
        commands.extend([{"$type": "send_vr_rig",
                         "frequency": "always"},
                         {"$type": "send_segmentation_colors"},
                         {"$type": "set_post_process",
                          "value": False},
                         {"$type": "set_render_quality",
                          "render_quality": 0},
                         {"$type": "attach_avatar_to_vr_rig",
                          "id": "a"},
                         {"$type": "send_id_pass_segmentation_colors",
                          "frequency": "always"}])
        # Send the commands.
        resp = self.communicate(commands)
        # Record the segmentation colors.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    self.segmentation_colors[segm.get_object_color(j)] = segm.get_object_name(j)
        # Loop until the Escape key is pressed.
        while not self.done:
            head_rotation = (0, 0, 0, 0)
            visible_objects = []
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse VR data.
                if r_id == "vrri":
                    vr_rig = VRRig(resp[i])
                    head_rotation = vr_rig.get_head_rotation()
                # Evaluate what objects are visible.
                elif r_id == "ipsc":
                    ipsc = IdPassSegmentationColors(resp[i])
                    for j in range(ipsc.get_num_segmentation_colors()):
                        color = ipsc.get_segmentation_color(j)
                        object_name = self.segmentation_colors[color]
                        visible_objects.append(object_name)
            # Record this frame.
            self.frame_data.append({"head_rotation": head_rotation,
                                    "visible_objects": visible_objects})
            # Advance to the next frame.
            resp = self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True
        # Write the record to disk.
        Path("log.json").write_text(dumps(self.frame_data))


if __name__ == "__main__":
    c = VRObservedObjects()
    c.run()
