from tdw.add_ons.sensor_interface_base import SensorInterfaceBase
from typing import List, Dict

class HapticGlove(SensorInterfaceBase):
    """
    Basic haptic glove nterface using haptic motors and DRV2605 haptic motor controllers.

    """

    def __init__(self, board_type: str = "Arduino Uno"):
        """
        :param board_type: The type of Arduino board being used.
        """

        super().__init__(board_type=board_type)

    def get_initialization_commands(self) -> List[dict]:
        self.commands = []
        self.commands.extend(super().get_initialization_commands())
        return self.commands

    def on_send(self, resp: List[bytes]) -> None:
        return


    def get_send_haptic_waveform_command(self, command_name: str, wave_id: int) -> Optional[dict]:
        return {"$type": "send_arduino_command",
                         "arduino_command_name": command_name,
                         "waveform_id": wave_id}


