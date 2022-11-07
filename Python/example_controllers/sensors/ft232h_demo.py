from tdw.controller import Controller
from tdw.add_ons.keyboard import Keyboard
from typing import List, Dict
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.ft232h_haptic_glove import FT232HHapticGlove
from tdw.sensors_data.finger import Finger
from tdw.sensors_data.waveform import Waveform
import time



class FT232HDemo(Controller):
    """
    Minimal example of sending vibration waveforms to 1-5 DRV2605 haptic 
    motor controllers from the FT232H using I2C. This will trigger a 
    vibration pattern from the "pancake" haptic motor connected to a controller, 
    attached to the fingers of the glove.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        self.glove = FT232HHapticGlove()
        self.add_ons.append(self.glove)
        keyboard.listen(key="Alpha1", function=self.wave_1)
        keyboard.listen(key="Alpha2", function=self.wave_2)
        keyboard.listen(key="Alpha3", function=self.wave_3)
        keyboard.listen(key="Alpha4", function=self.wave_4)        
        keyboard.listen(key="Alpha5", function=self.wave_5)
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def wave_1(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        waves = [Waveform.short_double_click_strong]
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky, Finger.index]
        self.glove.send_haptic_waveform(fingers, waves)

    def wave_2(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        waves = [Waveform.pulsing_strong]
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky, Finger.index]
        self.glove.send_haptic_waveform(fingers, waves)

    def wave_3(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        waves = [Waveform.buzz_1]
        # Which fingers do we want to vibrate?
        fingers = [Finger.index]
        self.glove.send_haptic_waveform(fingers, waves)

    def wave_4(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        waves = [Waveform.long_double_sharp_click_strong ]
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky, Finger.ring, Finger.middle, Finger.index, Finger.thumb]
        self.glove.send_haptic_waveform(fingers, waves)

    def wave_5(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        waves = [Waveform.transition_ramp_up_long_sharp]
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky, Finger.ring, Finger.middle, Finger.index, Finger.thumb]
        self.glove.send_haptic_waveform(fingers, waves)


if __name__ == "__main__":
    c = FT232HDemo(launch_build=False)
    while not c.done:
        c.communicate([])
    c.communicate({"$type": "terminate"})
