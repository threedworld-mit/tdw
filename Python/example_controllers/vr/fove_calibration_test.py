from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState
import time

"""
Minimal Fove Leap Motion example.
"""

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
g1_z = -0.15
g2_z = -0.4
g3_z = -0.65
xlt = -0.25
xmid = 0
xrt = 0.25
yup = 1.1
ymid = 1.0
ylow = 0.9
five_point_x_positions = [xlt, xmid, xrt, xlt, xrt, xlt, xmid, xrt, xlt, xrt, xlt,xmid, xrt, xlt, xrt]
five_point_y_positions = [yup, ymid, ylow, ylow, yup, yup, ymid, ylow, ylow, yup, yup, ymid, ylow, ylow, yup]
five_point_z_positions = [g1_z, g1_z, g1_z, g1_z, g1_z, g2_z, g2_z, g2_z, g2_z, g2_z, g3_z, g3_z, g3_z, g3_z, g3_z]

# Groups 1-3.
for i in range(15):
    commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                      object_id=Controller.get_unique_id(),
                                                      position={"x": x_positions[i], "y": y_positions[i], "z": five_point_z_position[i]},
                                                      scale_mass=False,
                                                      scale_factor={"x": 0.0127, "y": 0.0127, "z": 0.0127},
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
    # Reset albedo color of all objects to normal when gaze is not on any object.
    if (object_id is None):
        for id in om.transforms:
            c.communicate({"$type": "set_color", "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}, "id": id})
    else:
        # Highlight objects in blue when gaze is on them.
        c.communicate({"$type": "set_color", "color": {"r": 0, "g": 0, "b": 1.0, "a": 1.0}, "id": object_id})

c.communicate({"$type": "terminate"})
