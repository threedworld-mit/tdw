from typing import List
from json import dumps
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.vr import VR
from tdw.vr_data.rig_type import RigType


class VRObservedObjects(Controller):
    """
    Add several objects to the scene. Record which objects are visible to the VR agent.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        self.vr = VR(rig_type=RigType.oculus_touch, vr_rig_output_data=True, image_passes=["_id"])
        self.object_manager = ObjectManager(transforms=False, rigidbodies=False, bounds=False)
        keyboard = Keyboard()
        self.add_ons.extend([keyboard, self.object_manager, self.vr])
        keyboard.listen(key="Escape", function=self.quit)
        self.frame_data: List[dict] = list()

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the table object and make it kinematic.
        commands.extend(self.get_add_physics_object(model_name="small_table_green_marble",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0, "y": 0, "z": 0.5},
                                                    kinematic=True,
                                                    library="models_core.json"))
        # Add a box object.
        commands.extend(self.get_add_physics_object(model_name="woven_box",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0.2, "y": 1.0, "z": 0.5},
                                                    library="models_core.json"))
        # Add the ball object and make it graspable.
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0.2, "y": 3.0, "z": 0.5},
                                                    library="models_special.json",
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2}))
        self.communicate(commands)
        # Loop until the Escape key is pressed.
        while not self.done:
            visible_objects = []
            segmentation_colors = TDWUtils.get_segmentation_colors(id_pass=self.vr.images["_id"])
            for segmentation_color in segmentation_colors:
                # Convert to tuples to enable equality testing.
                sc = tuple(segmentation_color)
                for object_id in self.object_manager.objects_static:
                    if tuple(self.object_manager.objects_static[object_id].segmentation_color) == sc:
                        visible_objects.append(object_id)
                        break
            # Record this frame.
            self.frame_data.append({"head_rotation": self.vr.head.rotation,
                                    "visible_objects": visible_objects})
            # Advance to the next frame.
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True
        # Write the record to disk.
        Path("log.json").write_text(dumps(self.frame_data))


if __name__ == "__main__":
    c = VRObservedObjects()
    c.run()
