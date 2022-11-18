from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

"""
Minimal example of Oculus Leap Motion collision detection.
"""

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
    for finger in vr.left_hand_collisions:
        for bone in vr.left_hand_collisions[finger]:
            if len(vr.left_hand_collisions[finger][bone]) > 0:
                print(finger, bone, vr.left_hand_collisions[finger][bone])
