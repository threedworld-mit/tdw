from typing import List
from abc import ABC, abstractmethod
from overrides import final


class Agent(ABC):
    """
    An agent has a static state, a dynamic state, and can generate lists of commands given the dynamic state.
    """

    def __init__(self):
        """
        (no parameters)
        """

        """:field
        A list of commands to be sent on the next frame.
        """
        self.commands: List[dict] = list()
        # If True, this agent has already cached its static data.
        self._cached_static_data: bool = False

    @abstractmethod
    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per agent.

        :return: A list of commands that will initialize this agent.
        """

        raise Exception()

    @final
    def step(self, resp: List[bytes]) -> None:
        """
        Update the agent's state. Cache static data if needed and update the list of commands to send to the build.

        :param resp: The response from the build.
        """

        # Cache the static state.
        if not self._cached_static_data:
            self._cached_static_data = True
            self._cache_static_data(resp=resp)
        # Update the dynamic state.
        self._set_dynamic_data(resp=resp)
        # Get new commands.
        self.commands.extend(self._get_commands(resp=resp))

    def reset(self) -> None:
        """
        :return: Mark this agent as requiring a reset.
        """

        self._cached_static_data = False

    @abstractmethod
    def _cache_static_data(self, resp: List[bytes]) -> None:
        """
        Cache all required static data.

        :param resp: The response from the build.
        """

        raise Exception()

    @abstractmethod
    def _set_dynamic_data(self, resp: List[bytes]) -> None:
        """
        :param resp: The response from the build.

        :return: The updated agent state.
        """

        raise Exception()

    @abstractmethod
    def _get_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The response from the build.

        :return: A list of commands to send to the build, given the current state.
        """

        raise Exception()
