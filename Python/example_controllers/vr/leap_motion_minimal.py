from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.leap_motion import LeapMotion

"""
Minimal Oculus touch example.
"""

c = Controller(launch_build=False)
vr = LeapMotion()
c.add_ons.append(vr)
obj_id = Controller.get_unique_id()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_screen_size",
                           "width": 512,
                           "height": 512},
               c.get_add_object(model_name="rh10",
                                object_id=obj_id,
                                position={"x": 0, "y": 0, "z": 0.5})])
c.communicate([])
c.communicate({"$type": "set_leap_motion_graspable",
               "id": obj_id})
while True:
    c.communicate([])