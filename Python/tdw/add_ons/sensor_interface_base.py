from abc import ABC, abstractmethod
from typing import List, Union, Dict
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn


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


