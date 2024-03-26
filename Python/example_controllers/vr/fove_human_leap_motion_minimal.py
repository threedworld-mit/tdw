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
                                                  scale_factor={"x": 1.0, "y": 1.0, "z": 0.75},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": -0.25},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_flex.json"))
commands.extend(Controller.get_add_physics_object(model_name="zenblocks",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": 0},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.5, "y": 0.5, "z": 0.5},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend(Controller.get_add_physics_object(model_name="b03_cocacola_can_cage",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.4, "y": 1, "z": 0.01},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1.35, "y": 1.35, "z": 1.35},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_full.json"))
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": -0.3, "y": 1, "z": -0.07},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.85, "y": 0.85, "z": 0.85},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend(Controller.get_add_physics_object(model_name="champagne_cork",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.2, "y": 1, "z": -0.15},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1.25, "y": 1.25, "z": 1.25},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend(Controller.get_add_physics_object(model_name="mouse_02_vray",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.4, "y": 1, "z": -0.15},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1, "y": 1, "z": 1},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend(Controller.get_add_physics_object(model_name="rh10",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": -0.4, "y": 1, "z": -0.15},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend([{"$type": "set_post_process", "value": False}, 
                 {"$type": "set_target_framerate", "framerate": -1}])
vr = FoveHumanLeapMotion(position={"x": 0, "y": 1.195, "z": -0.475}, time_step=0.02, use_headset_position=False)
c.add_ons.append(vr)
c.communicate(commands)
while not vr.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
