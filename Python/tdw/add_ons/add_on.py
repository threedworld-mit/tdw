from typing import List
from abc import ABC, abstractmethod


class AddOn(ABC):
    """
    Controller add-ons can be "attached" to any controller to add functionality into the `communicate()` function.

    Add-ons work by reading the response from the build and building a list of commands to be sent on the next `Controller.communicate(commands)` call.
    Anything that add-ons do can be replicated elsewhere via the TDW Command API, which means that these add-ons don't provide _additional_ functionality to TDW; rather, they are utility objects for commonly required tasks such as image capture.

    We recommend that new TDW users use add-ons in their controllers, while more experienced users might prefer to have more fine-grained control. Add-ons are a new feature in TDW as of v1.9.0 and we're still in the process of updating our example controllers.

    To attach an add-on, append it to the `add_ons` list. Every time `Controller.communicate(commands)` is called, the add-on will evaluate the response from the build via `on_send(resp)`.
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
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        raise Exception()

    @abstractmethod
    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

        :param resp: The response from the build.
        """

        raise Exception()

    def before_send(self, commands: List[dict]) -> None:
        """
        This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

        :param commands: The commands that are about to be sent to the build.
        """

        pass
