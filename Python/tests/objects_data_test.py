from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms, Rigidbodies, Bounds, OutputData


"""
Test Transforms, Rigidbodies, and Bounds data.
"""


if __name__ == "__main__":
    c = Controller()
    commands = [TDWUtils.create_empty_room(20, 20)]
    object_ids = []
    # Add 5 objects.
    for i in range(5):
        o_id = c.get_unique_id()
        commands.append(c.get_add_object("trunck", object_id=o_id))
        object_ids.append(o_id)
    commands.extend([{"$type": "send_transforms",
                      "frequency": "always"},
                     {"$type": "send_rigidbodies",
                      "frequency": "always"},
                     {"$type": "send_bounds",
                      "frequency": "always"}])
    resp = c.communicate(commands)

    for r in resp[:-1]:
        r_id = OutputData.get_data_type_id(r)
        if r_id == "tran":
            print("TRANSFORMS")
            o = Transforms(r)
            for i in range(o.get_num()):
                assert o.get_id(i) in object_ids
                print(o.get_position(i))
                print(o.get_forward(i))
                print(o.get_rotation(i))
                print("")
            print("")
        elif r_id == "rigi":
            print("RIGIDBODIES")
            o = Rigidbodies(r)
            for i in range(o.get_num()):
                assert o.get_id(i) in object_ids
                print(o.get_sleeping(i))
                print(o.get_velocity(i))
                print(o.get_angular_velocity(i))
                print("")
            print("")
        elif r_id == "boun":
            print("BOUNDS")
            o = Bounds(r)
            for i in range(o.get_num()):
                assert o.get_id(i) in object_ids
                print(o.get_top(i))
                print(o.get_center(i))
                print(o.get_right(i))
                print(o.get_left(i))
                print(o.get_front(i))
                print(o.get_back(i))
                print(o.get_bottom(i))
                print("")
            print("")
    c.communicate({"$type": "terminate"})
