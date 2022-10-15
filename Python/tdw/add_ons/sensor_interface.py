from tdw.add_ons.sensor_interface_base import SensorInterfaceBase
from typing import List, Dict

class SensorInterface(SensorInterfaceBase):
    """
    Initialize basic sensor interface.

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





