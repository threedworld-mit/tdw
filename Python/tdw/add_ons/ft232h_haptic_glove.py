from abc import ABC, abstractmethod
from typing import List, Union, Dict, Optional
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.ft232h_interface_base import FT232HInterfaceBase
from tdw.sensors_data.finger import Finger
from tdw.sensors_data.waveform import Waveform
import adafruit_tca9548a
import adafruit_drv2605



class FT232HHapticGlove(FT232HInterfaceBase):
    """
    Basic haptic glove interface using 5 haptic motors, 5 DRV2605 haptic motor controllers
    and a TCA9548A 8-way i2C multiplexer.

    """

    def __init__(self):

        super().__init__()
 
        # Create the TCA9548A object and give it the I2C bus
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)

        # For each haptic feedback motor driver module, create it 
        # using the TCA9548A channel instead of the I2C object.
        self.drv_pinky = adafruit_drv2605.DRV2605(self.tca[0])
        self.drv_ring = adafruit_drv2605.DRV2605(self.tca[1])
        self.drv_middle = adafruit_drv2605.DRV2605(self.tca[2])
        self.drv_index = adafruit_drv2605.DRV2605(self.tca[3])
        self.drv_thumb = adafruit_drv2605.DRV2605(self.tca[4])

        self.drv_glove = [self.drv_pinky, self.drv_ring, self.drv_middle, self.drv_index, self.drv_thumb]

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """
        # Setup all motor controller chips in MODE_INTTRIG mode.
        for drv in self.drv_glove:
            drv.mode = 0
        self.commands = []
        return self.commands


    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """
        return
    
    def send_haptic_waveform(self, fingers: List[Finger], wave_sequence: List[Waveform]):
        """
        Send a list of one or more vibration waveforms to play in sequence (max 8), to a list
        of one or more fingers.
        """
        if len(fingers) > 5:
            print("Number of fingers > 5")
            return
        if len(wave_sequence) > 8:
            print("Wave sequence cannot exceed 8 waveforms")
            return
        for finger in fingers:
            # Fill slots with the waveform sequence.
            for i in range(len(wave_sequence)):
                self.drv_glove[finger.value].sequence[i] = adafruit_drv2605.Effect(wave_sequence[i].value)
            # Last empty slot (if there is one) should be zero.
            if i < 7:
                self.drv_glove[finger.value].sequence[i+1] = adafruit_drv2605.Effect(0)
            self.drv_glove[finger.value].play()
   
    def send_pause(self, fingers: List[Finger], duration: float = 0.5): 
        if len(fingers) > 5:
            print("Number of fingers > 5")
            return
        for finger in fingers:
            self.drv_glove[finger.value].Pause(duration)

