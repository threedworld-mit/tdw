from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.debug import Debug as DBug
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from time import sleep


"""
Create a controller with a `Debug` module.
After running a simple physics simulation, play back all of the commands.
"""


class Debug(Controller):
    def run(self):
        path: Path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("debug/debug.json")
        print(f"Debug log will be saved to: {path}")
        # Add a debug module.
        d = DBug(record=True, path=path)
        self.add_ons.append(d)
        self.start()
        o_id = self.get_unique_id()
        # Create the scene and add an object Set the mass of the object and apply a force..
        commands = [TDWUtils.create_empty_room(12, 12),
                    self.get_add_object("rh10",
                                        object_id=o_id),
                    {"$type": "set_mass",
                     "id": o_id,
                     "mass": 15},
                    {"$type": "rotate_object_by",
                     "axis": "pitch",
                     "id": o_id, "angle": 45},
                    {"$type": "apply_force_magnitude_to_object",
                     "id": o_id,
                     "magnitude": 250.0}]
        # Add the third-person camera.
        camera = ThirdPersonCamera(position={"x": 1, "y": 3, "z": 0},
                                   look_at=o_id)
        self.add_ons.append(camera)
        self.communicate(commands)
        # Keep looking at the object as it moves.
        for i in range(100):
            self.communicate([])
        sleep(1)
        # Remove the camera add-on.
        self.add_ons.remove(camera)
        # Play back all of the commands.
        d.record = False
        while len(d.playback) > 0:
            print(d.playback[0])
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    Debug().run()
