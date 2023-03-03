from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

"""
Minimal Oculus Leap Motion example.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
z = 0.8
table_id = Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=table_id,
                                                  position={"x": 0, "y": 0, "z": z},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="woven_box",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": z},
                                                  default_physics_values=False,
                                                  mass=100))
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1.25, "z": z}))
vr = OculusLeapMotion(non_graspable=[table_id])
c.add_ons.append(vr)
c.communicate(commands)
while True:
    c.communicate([])
