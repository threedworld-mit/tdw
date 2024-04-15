from tdw.controller import Controller
import numpy as np
from typing import List, Dict
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
from tdw.object_data.transform import Transform
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState
import time

"""
Fove eye/hand calibration protocol.
"""

def insert_position(eye: bool, index: int, position: np.ndarray):
    axis_0_index = 0 if eye else 1
    array[axis_0_index][index] = position

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend([{"$type": "set_physics_solver_iterations", "iterations": 15},
                 {"$type": "set_time_step", "time_step": 0.01}])
vr = FoveLeapMotion(position={"x": 0, "y": 1, "z": 0}, time_step=0.01)
c.add_ons.append(vr)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)
# Run FOVE spiral calibration.
commands = []
commands.append({"$type": "start_fove_calibration", "profile_name": "test"})
c.communicate(commands)
c.communicate([])

g1_z = -0.3
g2_z = -0.35
g3_z = -0.4
xlt = -0.125
xmid = 0
xrt = 0.125
yup = 0.9
ymid = 0.8
ylow = 0.7
five_pnt_x_pos = [xlt, xmid, xrt, xlt, xrt, xlt + 0.0175, xmid, xrt - 0.0175, xlt + 0.0175, xrt - 0.0175, xlt + 0.025, xmid, xrt - 0.025, xlt + 0.025, xrt - 0.025]
five_pnt_y_pos = [yup, ymid, ylow, ylow, yup, yup, ymid, ylow, ylow, yup, yup, ymid, ylow, ylow, yup]
five_pnt_z_pos = [g1_z, g1_z, g1_z, g1_z, g1_z, g2_z, g2_z, g2_z, g2_z, g2_z, g3_z, g3_z, g3_z, g3_z, g3_z]
sphere_ids = []
sphere_ids_static = []
touch_time = 0.5
timer_started = False
array = np.zeros(shape=(2, 15, 3))
saved_data = False

commands = []
# Create sphere groups 1-3.
for i in range(15):
    obj_id = Controller.get_unique_id()
    sphere_ids.append(obj_id)
    commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                      object_id=obj_id,
                                                      position={"x": five_pnt_x_pos[i], "y": five_pnt_y_pos[i], "z": five_pnt_z_pos[i]},
                                                      scale_mass=True,
                                                      scale_factor={"x": 0.025, "y": 0.025, "z": 0.025},
                                                      default_physics_values=False,
                                                      mass=1.0,
                                                      dynamic_friction=1.0,
                                                      static_friction=1.0,
                                                      bounciness=0,
                                                      kinematic=True,
                                                      gravity=False,
                                                      library="models_flex.json"))
c.communicate(commands)
# Make a static copy of the sphere ID list, for indexing reference. 
sphere_ids_static = sphere_ids.copy()
while not vr.done:
    commands = []
    for sphere_id in sphere_ids: 
        touching = False
        for bone in vr.right_hand_collisions:
            if sphere_id in vr.right_hand_collisions[bone]:
                touching = True
                # Start half-second timer.
                if timer_started == False: 
                    start_time = time.time()
                    timer_started = True
                    #gaze_depth_list.clear()
                break
        if touching:
            if timer_started:
                curr_time = time.time()
            if  (curr_time - start_time) < touch_time:
                # Touch event is still within defined duration, so keep it blue.
                color = {"r": 0, "g": 0, "b": 1.0, "a": 1.0}
                # Store eye tracking data for the user looking at this sphere.
                insert_position(True, sphere_ids_static.index(sphere_id), vr.converged_eyes.gaze_position)
                # Store finger position as well.
                insert_position(False, sphere_ids_static.index(sphere_id), vr.right_hand_transforms[bone].position)
            else:
                # User touched this sphere for the defined duration, so end touch event and remove sphere ID from use.
                #commands.append({"$type": "set_object_visibility", "id": sphere_id, "visible": False})
                commands.append({"$type": "hide_object", "id": sphere_id})
                sphere_ids.remove(sphere_id)
                #gaze_depth_list.clear()              
                timer_started = False
        else:
            # Reset color if sphere is still active and not being touched.
            if sphere_id in sphere_ids:
                color = {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}
        commands.append({"$type": "set_color", "color": color, "id": sphere_id})
    c.communicate(commands)
    if (len(sphere_ids)) == 0:
        # All spheres have been touched, so write out the stored data array. 
        # If we do the averaging, we would do it here.
        if not saved_data:
            with open('C:\\Users\\weiwe\\OneDrive\\Documents\\eye_hand_data\\arr_' + str(time.time()) + ".npy", 'wb') as f:
                np.save(f, array)
                saved_data = True

c.communicate({"$type": "terminate"})
