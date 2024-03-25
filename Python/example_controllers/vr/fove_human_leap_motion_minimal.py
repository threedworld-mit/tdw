from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_human_leap_motion import FoveHumanLeapMotion

"""
Minimal Fove Leap Motion example.
"""

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 0, "z": 0},
                                                  scale_factor={"x": 1.0, "y": 1.0, "z": 1.0},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": -0.25},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_flex.json"))
commands.extend([{"$type": "set_post_process", "value": False}, 
                 {"$type": "set_target_framerate", "framerate": -1}])
vr = FoveHumanLeapMotion(position={"x": 0, "y": 0.685, "z": -1.05}, time_step=0.02)
c.add_ons.append(vr)
c.communicate(commands)
while not vr.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
