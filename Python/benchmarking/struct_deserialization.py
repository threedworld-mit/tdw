from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark


"""
Benchmark the speed of deserializing structs (such as Vector3 and Quaternion).
"""

if __name__ == "__main__":
    o_id = 0
    cmds = [{"$type": "teleport_object",
             "position": {"x": 0, "y": 0, "z": 0},
             "id": o_id},
            {"$type": "rotate_object_to",
             "rotation": {"w": 1, "x": 0, "y": 0, "z": 0},
             "id": o_id}]
    c = Controller(launch_build=False)
    b = Benchmark()
    c.add_ons.append(b)
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object("rh10", object_id=o_id)])
    b.start()
    for i in range(5000):
        c.communicate(cmds)
    b.stop()
    print(f"FPS: {round(b.fps)}")
    c.communicate({"$type": "terminate"})
