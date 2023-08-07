from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

"""
Minimal Oculus Leap Motion example.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
z = 0.6
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 0, "z": z},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": z - 0.25},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_flex.json"))
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(commands)
while not vr.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
