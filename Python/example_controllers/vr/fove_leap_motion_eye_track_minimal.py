from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
from tdw.vr_data.fove.eye import Eye

"""
Minimal Fove Leap Motion example.
"""

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
table_id = Controller.get_unique_id()
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=table_id,
                                                  position={"x": 0, "y": 0, "z": 0},
                                                  scale_factor={"x": 1.0, "y": 1.0, "z": 0.75},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": -0.2},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_flex.json"))
commands.extend(Controller.get_add_physics_object(model_name="baseball",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": 0},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1, "y": 1, "z": 1},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_full.json"))
commands.extend(Controller.get_add_physics_object(model_name="b03_cocacola_can_cage",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.145, "y": 1, "z": 0.07},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1.35, "y": 1.35, "z": 1.35},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_full.json"))
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": -0.25, "y": 1, "z": -0.02},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.85, "y": 0.85, "z": 0.85},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.2, "y": 1, "z": -0.15},
                                                  scale_mass=False,
                                                  scale_factor={"x": 1, "y": 1, "z": 1},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_core.json"))
commands.extend(Controller.get_add_physics_object(model_name="mouse_02_vray",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0.433, "y": 1, "z": -0.15},
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
vr = FoveLeapMotion(position={"x": 0, "y": 1.195, "z": -0.475}, time_step=0.02)
c.add_ons.append(vr)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)

while not vr.done:
    resp=c.communicate([])
    object_id = vr.converged_eyes.gaze_id
    # Reset albedo color of all objects to normal when gaze is not on any object, or on the table.
    if (object_id is None) or (object_id == table_id):
        for id in om.transforms:
            c.communicate({"$type": "set_color", "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}, "id": id})
    else:
        # Highlight objects blue when gaze is on them.
        c.communicate({"$type": "set_color", "color": {"r": 0, "g": 0, "b": 1.0, "a": 1.0}, "id": object_id})

c.communicate({"$type": "terminate"})
