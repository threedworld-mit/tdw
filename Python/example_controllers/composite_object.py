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
        self.start()
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Find the local asset bundle for this platform.
        url = str(Path("composite_objects/" + platform.system() + "/test_composite_object").resolve())

        # Add the local object.
        o_id = self.get_unique_id()
        self.communicate([{"$type": "add_object",
                           "name": "test_composite_object",
                           "url": url,
                           "scale_factor": 1,
                           "id": o_id},
                          {"$type": "set_mass",
                           "id": o_id,
                           "mass": 100}])

        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 1.49, "z": -2.77}))

        # Test that each sub-object has a unique segmentation color.
        resp = self.communicate({"$type": "send_segmentation_colors",
                                 "ids": []})
        colors = SegmentationColors(resp[0])
        segmentation_colors = []
        # There are 4 objects: The parent object, the motor, the "base" of the motor, and the light.
        assert colors.get_num() == 4, colors.get_num()
        print("Segmentation colors:")
        for i in range(colors.get_num()):
            print(colors.get_object_id(i), colors.get_object_color(i))

            # Cache the color for the next test.
            segmentation_colors.append(colors.get_object_color(i))

        # Test that each sub-object is visible to the avatar.
        resp = self.communicate({"$type": "send_id_pass_segmentation_colors",
                                 "frequency": "once"})
        colors = IdPassSegmentationColors(resp[0])
        # There are three visible objects (the light won't be visible in the _id pass).
        assert colors.get_num_segmentation_colors() == 3

        print("\nObserved colors:")

        # Test that the colors observed by the avatar are in the cache.
        for i in range(colors.get_num_segmentation_colors()):
            observed_color = colors.get_segmentation_color(i)
            assert observed_color in segmentation_colors
            print(observed_color)

        # Get composite objects data.
        resp = self.communicate({"$type": "send_composite_objects"})
        assert len(resp) > 1
        assert OutputData.get_data_type_id(resp[0]) == "comp"

        o = CompositeObjects(resp[0])
        assert o.get_num() == 1
        # There are 3 sub-objects: The motor, the "base" of the motor, and the light.
        assert o.get_num_sub_objects(0) == 3

        print("\nCompositeObjects: ")

        commands = []
        lights = []

        # Iterate through each sub-object.
        for s in range(o.get_num_sub_objects(0)):
            sub_object_id = o.get_sub_object_id(0, s)
            s_type = o.get_sub_object_machine_type(0, s)
            print(sub_object_id, s_type)

            # Add commands depending on the type of sub-object.
            if s_type == "motor":
                # Start the motor.
                commands.append({"$type": "set_motor",
                                 "target_velocity": 500,
                                 "force": 500,
                                 "id": sub_object_id})
            elif s_type == "light":
                commands.append({"$type": "set_sub_object_light",
                                 "is_on": True,
                                 "id": sub_object_id})
                lights.append(sub_object_id)

        self.communicate(commands)

        is_on = True
        for i in range(1000):
            commands = []
            # Every 50 frames, blink the lights on and off.
            if i % 50 == 0:
                is_on = not is_on
                for light in lights:
                    commands.append({"$type": "set_sub_object_light",
                                     "is_on": is_on,
                                     "id": light})
            else:
                commands.append({"$type": "do_nothing"})
            self.communicate(commands)


if __name__ == "__main__":
    CompositeObject().run()
