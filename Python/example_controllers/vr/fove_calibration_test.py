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
commands.extend([{"$type": "set_physics_solver_iterations", "iterations": 15},
                 {"$type": "set_time_step", "time_step": 0.01}])
g1_z = -0.3
g2_z = -0.4
g3_z = -0.5
xlt = -0.15
xmid = 0
xrt = 0.15
yup = 1.1
ymid = 1.0
ylow = 0.9
five_pnt_x_pos = [xlt, xmid, xrt, xlt, xrt, xlt, xmid, xrt, xlt, xrt, xlt,xmid, xrt, xlt, xrt]
five_pnt_y_pos = [yup, ymid, ylow, ylow, yup, yup, ymid, ylow, ylow, yup, yup, ymid, ylow, ylow, yup]
five_pnt_z_pos = [g1_z, g1_z, g1_z, g1_z, g1_z, g2_z, g2_z, g2_z, g2_z, g2_z, g3_z, g3_z, g3_z, g3_z, g3_z]
sphere_ids = []
touch_time = 0.5

# Groups 1-3.
for i in range(15):
    obj_id = Controller.get_unique_id()
    sphere_ids.append(obj_id)
    commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                      object_id=obj_id,
                                                      position={"x": five_pnt_x_pos[i], "y": five_pnt_y_pos[i], "z": five_pnt_z_pos[i]},
                                                      scale_mass=False,
                                                      scale_factor={"x": 0.025, "y": 0.025, "z": 0.025},
                                                      default_physics_values=False,
                                                      mass=1.0,
                                                      dynamic_friction=1.0,
                                                      static_friction=1.0,
                                                      bounciness=0,
                                                      kinematic=True,
                                                      gravity=False,
                                                      library="models_flex.json"))
vr = FoveLeapMotion(position={"x": 0, "y": 1, "z": 0}, time_step=0.01)
c.add_ons.append(vr)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)

timer_started = False
calibration_started = False   
while not vr.done:
    commands = []
    for sphere_id in sphere_ids: 
        touching = False
        for bone in vr.right_hand_collisions:
            if sphere_id in vr.right_hand_collisions[bone]:
                touching = True
                if timer_started == False: 
                    start_time = time.time()
                    timer_started = True
                break
        if touching:
            if timer_started:
                curr_time = time.time()
            if  (curr_time - start_time) < touch_time:
                # Touch event is still under defined duration, so keep it blue.
                color = {"r": 0, "g": 0, "b": 1.0, "a": 1.0}
                # Store eye tracking data for the user looking at this sphere.
                print(" Dir = " + str(vr.converged_eyes.direction) + ", depth = " + str(vr.combined_depth))
            else:
                # User touched this sphere for the defined duration, so render it inactive.
                commands.append({"$type": "set_object_visibility", "id": sphere_id, "visible": False})
                sphere_ids.remove(sphere_id)
                timer_started = False
        else:
            # Reset color if sphere is still active and not being touched.
            if sphere_id in sphere_ids:
                color = {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}
        commands.append({"$type": "set_color", "color": color, "id": sphere_id})
    c.communicate(commands)
    commands = []
    if (len(sphere_ids)) == 0:
        # All spheres have been touched, so start calibration using the stored eye tracking data.
        if not calibration_started:
            calibration_started = True
            commands.append({"$type": "start_fove_calibration", "profile_name": "test"})
    c.communicate(commands)

c.communicate({"$type": "terminate"})
