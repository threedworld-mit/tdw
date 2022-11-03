from tdw.controller import Controller
from typing import List, Dict
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.ft232h_haptic_glove import FT232HHapticGlove
from tdw.sensors_data.finger import Finger
from tdw.sensors_data.waveform import Waveform
import time

"""
Minimal example of sending vibration waveforms to 1-5 DRV2605 haptic 
motor controllers from the FT232H using I2C. This will trigger a 
vibration pattern from the "pancake" haptic motor connected to a controller, 
attached to the fingers of the glove.

"""

c = Controller(launch_build=False)
glove = FT232HHapticGlove()
c.add_ons.append(glove)
c.communicate(TDWUtils.create_empty_room(12, 12))

# We can use from 1 to 8 of the defined waveforms in sequence.
waves = [Waveform.buzz_1]
# Which fingers do we want to vibrate?
fingers = [Finger.pinky, Finger.index]

for i in range(10):
    glove.send_haptic_waveform(fingers, waves)
    time.sleep(1.0)
c.communicate({"$type": "terminate"})
