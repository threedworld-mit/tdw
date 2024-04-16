from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.output_data import OutputData, Fove
from tdw.add_ons.object_manager import ObjectManager
import time

"""
Fove eye/hand calibration protocol.
"""

c = Controller(launch_build=False)
commands = [TDWUtils.create_empty_room(12, 12)]
fove = FoveLeapMotion(position={"x": 0, "y": 1, "z": 0}, 
                                time_step=0.01, 
                                calibration_data_path="C:\\Users\\weiwe\\OneDrive\\Documents\\eye_hand_data\\eye_hand_data_" + str(time.time))
c.add_ons.append(fove)
om = ObjectManager()
c.add_ons.append(om)
c.communicate(commands)

while not fove.done:
    if fove.calibration_state == CalibrationState.running:
        fove.initialize_scene()
    c.communicate([])
   
c.communicate({"$type": "terminate"})
