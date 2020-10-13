from json import dumps
from time import time
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


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
    print(f"Byte size: {len(dumps(cmds).encode('utf-8'))}")

    c = Controller()

    c.start()
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object("rh10", object_id=o_id)])
    num_trials = 5000
    t0 = time()
    for i in range(num_trials):
        c.communicate(cmds)
    fps = (num_trials / (time() - t0))
    print(f"FPS: {round(fps)}")
    c.communicate({"$type": "terminate"})
