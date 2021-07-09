from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.debug import Debug as DBug
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
        self.communicate(TDWUtils.create_empty_room(12, 12))

        o_id = self.add_object("rh10")

        self.communicate(TDWUtils.create_avatar(position={"x": 1, "y": 3, "z": 0}))

        self.communicate([{"$type": "set_mass",
                           "id": o_id,
                           "mass": 15},
                          {"$type": "rotate_object_by",
                           "axis": "pitch",
                           "id": o_id, "angle": 45},
                          {"$type": "apply_force_magnitude_to_object",
                           "id": o_id,
                           "magnitude": 250.0}])
        for i in range(100):
            self.communicate({"$type": "look_at",
                              "avatar_id": "a",
                              "object_id": o_id})
        sleep(1)
        # Print the recorded commands to the console.
        for commands in d.playback:
            print(commands)

        # Play back all of the commands.
        d.record = False
        while len(d.playback) > 0:
            print(d.playback)
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    Debug().run()
