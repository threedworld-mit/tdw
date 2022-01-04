from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, CompositeObjects, IdPassSegmentationColors, SegmentationColors
from pathlib import Path
import platform


"""
Create a composite object from a local asset bundle.
Test that the object loaded correctly.
Apply sub-object commands to the sub-objects.
"""


class CompositeObject(Controller):
    def run(self):
        commands = [TDWUtils.create_empty_room(12, 12)]

        # Find the local asset bundle for this platform.
        url = "file:///" + str(Path("composite_objects/" + platform.system() + "/test_composite_object").resolve())

        # Add the local object.
        o_id = self.get_unique_id()
        commands.extend([{"$type": "add_object",
                          "name": "test_composite_object",
                          "url": url,
                          "scale_factor": 1,
                          "id": o_id},
                         {"$type": "set_mass",
                          "id": o_id,
                          "mass": 100},
                         {"$type": "send_segmentation_colors"},
                         {"$type": "send_id_pass_segmentation_colors"},
                         {"$type": "send_composite_objects"},
                         {"$type": "send_rigidbodies",
                          "frequency": "always"}])
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1.49, "z": -2.77}))
        resp = self.communicate(commands)

        visible_objects = dict()
        segmentation_colors = dict()
        # Get all objects.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    object_id = segm.get_object_id(j)
                    visible_objects[object_id] = False
                    segmentation_colors[segm.get_object_color(j)] = object_id
        # Get all visible objects. Also, get the ID of the light and motor sub-objects.
        light_id = -1
        motor_id = -1
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "ipsc":
                ipsc = IdPassSegmentationColors(resp[i])
                for j in range(ipsc.get_num_segmentation_colors()):
                    object_color = ipsc.get_segmentation_color(j)
                    object_id = segmentation_colors[object_color]
                    visible_objects[object_id] = True
            elif r_id == "comp":
                comp = CompositeObjects(resp[i])
                for j in range(comp.get_num()):
                    object_id = comp.get_object_id(j)
                    if object_id == o_id:
                        for k in range(comp.get_num_sub_objects(j)):
                            sub_object_id = comp.get_sub_object_id(j, k)
                            sub_object_machine_type = comp.get_sub_object_machine_type(j, k)
                            if sub_object_machine_type == "light":
                                light_id = sub_object_id
                            elif sub_object_machine_type == "motor":
                                motor_id = sub_object_id
        print(visible_objects)
        # Start the motor and turn the light on.
        is_on = True
        self.communicate([{"$type": "set_motor",
                           "target_velocity": 500,
                           "force": 500,
                           "id": motor_id},
                          {"$type": "set_sub_object_light",
                           "is_on": is_on,
                           "id": light_id}])
        for i in range(1000):
            # Every 50 frames, blink the lights on and off.
            if i % 50 == 0:
                is_on = not is_on
                self.communicate({"$type": "set_sub_object_light",
                                  "is_on": is_on,
                                  "id": light_id})
            else:
                self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    CompositeObject().run()
