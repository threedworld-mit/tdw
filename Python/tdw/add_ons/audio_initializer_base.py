from abc import ABC, abstractmethod
from typing import List
from overrides import final
from tdw.add_ons.add_on import AddOn


class AudioInitializerBase(AddOn, ABC):
    """
    Abstract base class for an audio initializer add-on.
    """

    def __init__(self, avatar_id: str = "a", framerate: int = 60):
        """
        :param avatar_id: The ID of the listening avatar.
        :param framerate: The target simulation framerate.
        """

        super().__init__()
        """:field
        The ID of the listening avatar.
        """
        self.avatar_id: str = avatar_id
        # The target framerate.
        self._target_framerate: int = framerate

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        return [{"$type": "set_target_framerate",
                 "framerate": self._target_framerate},
                {"$type": self._get_sensor_command_name(),
                 "avatar_id": self.avatar_id}]

    @final
    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

        return

    @abstractmethod
    def _get_sensor_command_name(self) -> str:
        """
        :return: The name of the command to add an audio sensor.
        """

        raise Exception()
