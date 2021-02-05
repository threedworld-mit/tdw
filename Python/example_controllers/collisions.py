from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.collisions import Collisions

"""
Receive collision output data and read it as a `Collisions` object.
"""

if __name__ == "__main__":
    c = Controller(launch_build=False)
    c.start()
    resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                          c.get_add_object(model_name="rh10", position={"x": 0, "y": 1, "z": 0}, object_id=0),
                          c.get_add_object(model_name="rh10", position={"x": 0, "y": 2, "z": 0}, object_id=1),
                          {"$type": "send_collisions",
                           "enter": True,
                           "stay": True,
                           "exit": True,
                           "collision_types": ["obj", "env"]}])

    for i in range(200):
        # Read collision data.
        collisions = Collisions(resp=resp)
        # Only print to the console if there were any collisions on this frame.
        if len(collisions.obj_collisions) > 0 and len(collisions.env_collisions) > 0:
            print(f"Frame {i}")
            if len(collisions.obj_collisions) > 0:
                print("\tObject-object collisions")
                for ids in collisions.obj_collisions:
                    state = collisions.obj_collisions[ids].state
                    print(f"\t\t{ids}\t{state}")
            if len(collisions.env_collisions) > 0:
                print("\tObject-environment collisions")
                for object_id in collisions.env_collisions:
                    state = collisions.env_collisions[object_id].state
                    print(f"\t\t{object_id}\t{state}")

        # Advance another frame.
        resp = c.communicate([])
    c.communicate({"$type": "terminate"})
