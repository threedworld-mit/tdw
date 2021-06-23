from typing import List
from abc import ABC, abstractmethod


class ControllerModule(ABC):
    """
    Controller modules can be added to any controller to add functionality into the `communicate()` function.
    """

    def __init__(self):
        """
        (no parameters)
        """

        """:field
        These commands will be appended to the commands of the next `communicate()` call.
        """
        self.commands: List[dict] = list()
        """:field
        If True, this module has been initialized.
        """
        self.initialized: bool = False

    @abstractmethod
    def get_initialization_commands(self) -> List[dict]:
        """
        :return: A list of commands that will initialize this module.
        """

        raise Exception()

    @abstractmethod
    def on_communicate(self, resp: List[bytes], commands: List[dict]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        :param resp: The response from the build.
        :param commands: All of the commands that were just sent to the build.
        """

        raise Exception()
