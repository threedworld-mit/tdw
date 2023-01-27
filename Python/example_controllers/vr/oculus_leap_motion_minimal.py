from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

"""
Minimal Oculus Leap Motion example.
"""

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 0, "z": 0.5},
                                                  kinematic=True,))
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.2, "y": 1.0, "z": 0.5}))
c.communicate(commands)
while True:
    c.communicate([])
