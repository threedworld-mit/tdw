from tdw.controller import Controller
from tdw.add_ons.keyboard import Keyboard
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.haptic_glove import HapticGlove
from tdw.sensors_data.finger import Finger
from tdw.sensors_data.waveform import Waveform
import time


class ArduinoGloveDemo(Controller):
    """
    Minimal example of sending a custom command to an Arduino, to control 
    a DRV2605 haptic motor controller. This will trigger a vibration pattern from 
    a "pancake" haptic motor connected to the controller.
    The command name "playSequence" is registered in the Arduino code using
    this line:

    uduino.addCommand("playSequence", playSeq);

    When TDW sends the "playSequence" command, the function "playSeq" is invoked, 
    which sends the requested vibration waveform to the haptic motor.
"""
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        self.glove = HapticGlove()
        self.add_ons.append(self.glove)
        keyboard.listen(key="Alpha1", function=self.wave_1)
        keyboard.listen(key="Alpha2", function=self.wave_2)
        keyboard.listen(key="Alpha3", function=self.wave_3)
        keyboard.listen(key="Alpha4", function=self.wave_4)        
        keyboard.listen(key="Alpha5", function=self.wave_5)
        keyboard.listen(key="Escape", function=self.quit)
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def quit(self):
        self.done = True

    def wave_1(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        wave = Waveform.short_double_click_strong.value
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky.value, Finger.index.value]
        self.communicate(self.glove.get_send_haptic_glove_command(wave_id=wave, fingers=fingers))

    def wave_2(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        wave = Waveform.pulsing_strong.value
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky.value, Finger.index.value]
        self.communicate(self.glove.get_send_haptic_glove_command(wave_id=wave, fingers=fingers))

    def wave_3(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        wave = Waveform.buzz_1.value
        # Which fingers do we want to vibrate?
        fingers = [Finger.index.value]
        self.communicate(self.glove.get_send_haptic_glove_command(wave_id=wave, fingers=fingers))

    def wave_4(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        wave = Waveform.long_double_sharp_click_strong.value 
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky.value, Finger.ring.value, Finger.middle.value, Finger.index.value, Finger.thumb.value]
        self.communicate(self.glove.get_send_haptic_glove_command(wave_id=wave, fingers=fingers))

    def wave_5(self):      
        # We can use from 1 to 8 of the defined waveforms in sequence.
        wave = Waveform.transition_ramp_up_long_sharp.value
        # Which fingers do we want to vibrate?
        fingers = [Finger.pinky.value, Finger.ring.value, Finger.middle.value, Finger.index.value, Finger.thumb.value]
        self.communicate(self.glove.get_send_haptic_glove_command(wave_id=wave, fingers=fingers))


if __name__ == "__main__":
    c = ArduinoGloveDemo(launch_build=False)
    while not c.done:
        c.communicate([])
    c.communicate({"$type": "terminate"})

