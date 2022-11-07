from abc import ABC, abstractmethod
from typing import List, Union, Dict, Optional
from pathlib import Path
from enum import Enum
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from os import environ
# Note we need to set the environment variables BEFORE we try to import the "board" library!
environ["BLINKA_FT232H"] = "1"
environ["BLINKA_MCP2221"] = "1"
import board
import busio
import digitalio
from time import sleep



class FT232HInterfaceBase(AddOn, ABC):
    """
    Abstract base class for sensor or haptic interface add-ons, based on an FT222H
    usb-to-serial converter and using the i2C protocol. This add-on is 100% Python and does
    not involve any C# commands on the build side.
    """

    def __init__(self):

        super().__init__()
 
        # Create I2C bus as normal
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """
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



