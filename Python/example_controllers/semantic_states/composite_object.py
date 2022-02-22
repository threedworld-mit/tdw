from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.add_ons.object_manager import ObjectManager
from pathlib import Path
import platform


class CompositeObject(Controller):
    """
    Create a composite object from a local asset bundle. Apply sub-object commands to the sub-objects.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.composite_object_manager = CompositeObjectManager()
        self.object_manager = ObjectManager(transforms=False, rigidbodies=True, bounds=False)
        self.add_ons.extend([self.object_manager, self.composite_object_manager])

    def run(self):
        # Reset the add-ons.
        self.object_manager.reset()
        self.composite_object_manager.reset()
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
                          "mass": 100}])
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1.49, "z": -2.77}))
        self.communicate(commands)
        light_id = - 1
        motor_id = -1
        for object_id in self.composite_object_manager.static:
            if object_id == o_id:
                # Get the ID of the first motor.
                motor_id = list(self.composite_object_manager.static[object_id].motors.keys())[0]
                # Get the ID of the first light.
                light_id = list(self.composite_object_manager.static[object_id].lights.keys())[0]
                break
        # Get the current status of the light and motor.
        is_on = self.composite_object_manager.dynamic[o_id].lights[light_id].is_on
        force = self.composite_object_manager.static[o_id].motors[motor_id].force
        # Start the motor and turn the light on.
        self.communicate([{"$type": "set_motor_target_velocity",
                           "target_velocity": 500,
                           "id": motor_id},
                          {"$type": "set_motor_force",
                           "force": force + 500,
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
