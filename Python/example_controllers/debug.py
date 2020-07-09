from tdw.tdw_utils import TDWUtils
from tdw.debug_controller import DebugController
from time import sleep


"""
Create a debug controller. After running a simple physics simulation, play back all of the commands.
"""


class Debug(DebugController):
    def run(self):
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
        for commands in self.record:
            print(commands)

        # Play back all of the commands.
        self.playback()


if __name__ == "__main__":
    Debug().run()
