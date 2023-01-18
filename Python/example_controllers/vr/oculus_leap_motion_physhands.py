from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

"""
Minimal Oculus Leap Motion example.
"""

c = Controller(launch_build=False)
vr = OculusLeapMotion(attach_avatar=False, set_graspable=False)
c.add_ons.append(vr)
obj_id = Controller.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=obj_id,
                                position={"x": 0, "y": 0, "z": 0.5}),
               {"$type": "set_object_collision_detection_mode", 
                "id": obj_id, 
                "mode": "discrete"}])
c.communicate({"$type": "set_teleportation_area"})
while True:
    c.communicate([])
