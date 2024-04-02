from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState

"""
Minimal Fove Leap Motion example.
"""

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
x_positions = [-0.35, 0, 0.35, -0.35, 0, 0.35]
y_positions = [1.1, 1.1, 1.1, 0.9, 0.9, 0.9]

table_id = Controller.get_unique_id()
# Group 1.
for i in range(6):
    commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                      object_id=Controller.get_unique_id(),
                                                      position={"x": x_positions[i], "y": y_positions[i], "z": -0.75},
                                                      scale_mass=False,
                                                      scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                      kinematic=True,
                                                      gravity=False,
                                                      library="models_flex.json"))
# Group 2
for i in range(6):
    commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                      object_id=Controller.get_unique_id(),
                                                      position={"x": x_positions[i], "y": y_positions[i], "z": -1.25},
                                                      scale_mass=False,
                                                      scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                      kinematic=True,
                                                      gravity=False,
                                                      library="models_flex.json"))
vr = FoveLeapMotion(position={"x": 0, "y": 1, "z": 0}, time_step=0.02)
c.add_ons.append(vr)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)

while not vr.done:
    resp=c.communicate([])
    # Use the appropriate gaze ray based on eye state.
    if vr.left_eye.state == EyeState.closed and vr.right_eye.state == EyeState.opened:
        object_id = vr.right_eye.gaze_id
    elif vr.right_eye.state == EyeState.closed and vr.left_eye.state == EyeState.opened:
        object_id = vr.left_eye.gaze_id
    else:
        object_id = vr.converged_eyes.gaze_id
    # Reset albedo color of all objects to normal when gaze is not on any object, or on the table.
    if (object_id is None) or (object_id == table_id):
        for id in om.transforms:
            c.communicate({"$type": "set_color", "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}, "id": id})
    else:
        # Highlight objects in blue when gaze is on them.
        c.communicate({"$type": "set_color", "color": {"r": 0, "g": 0, "b": 1.0, "a": 1.0}, "id": object_id})

c.communicate({"$type": "terminate"})
