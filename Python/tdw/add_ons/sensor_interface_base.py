from abc import ABC, abstractmethod
from typing import List, Union, Dict, Optional
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.sensors_data.analog_pin import AnalogPin
from tdw.sensors_data.pin_mode import PinMode
from tdw.sensors_data.finger import Finger


class SensorInterfaceBase(AddOn, ABC):
    """
    Abstract base class for sensor or haptic interface add-ons.
    """

    def __init__(self, board_type: str = "Arduino Uno"):
        """
        :param board_type: The type of Arduino board being used.
        """

        super().__init__()
        """:field
        The type of Arduino board in use.
        """
        self.board_type: str = board_type

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """
        self.commands = []
        self.commands.append({"$type": "create_sensor_interface",
                              "board_type": self.board_type})
        return self.commands


    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """
        return

    def get_digital_read_command(self, pin: int) -> Optional[dict]:
        return {"$type": "digital_read",
                "digital_pin": pin}

    def get_digital_write_command(self, pin: int, pin_mode: PinMode, value: int) -> Optional[dict]:
        return {"$type": "digital_write",
                "digital_pin": pin,
                "pin_mode": pin_mode,
                "value": value}

    def get_analog_read_command(self, pin: AnalogPin) -> Optional[dict]:
        return{"$type": "analog_read",
               "analog_pin": pin}

    def get_analog_pwm_write_command(self, pin: int, value: int):
        return {"$type": "analog_pwm_write",
                "digital_pin": pin,
                "value": value}

    def get_analog_servo_write_command(self, pin: int, value: int):
        return {"$type": "analog_servo_write",
                "digital_pin": pin,
                "value": value}

    def get_send_arduino_command(self, command_name: str) -> Optional[dict]:
        return {"$type": "send_arduino_command",
                "arduino_command_name": command_name}
    """
    def get_send_haptic_glove_command(self, wave_id: int, fingers: List[str]) -> Optional[dict]:
        return {"$type": "send_haptic_glove_command",
                "waveform_id": wave_id,
                "fingers": fingers}
    """
    def get_send_haptic_glove_command(self, wave_id: int) -> Optional[dict]:
        return {"$type": "send_haptic_glove_command",
                "waveform_id": wave_id}