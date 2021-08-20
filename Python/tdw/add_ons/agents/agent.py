from typing import List, Dict
from abc import ABC, abstractmethod
from overrides import final
from tdw.add_ons.manager import Manager


class Agent(ABC):
    def __init__(self):
        super().__init__()
        self.cached_static_data: bool = False
        self.commands: List[dict] = list()

    @abstractmethod
    def get_required_managers(self) -> Dict[str, Manager]:
        raise Exception()

    @abstractmethod
    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per agent.

        :return: A list of commands that will initialize this agent.
        """

        raise Exception()

    @final
    def step(self, resp: List[bytes]) -> None:
        # Cache the static state.
        if not self.cached_static_data:
            self.cached_static_data = True
            self._cache_static_data(resp=resp)
        # Update the dynamic state.
        self._set_dynamic_data(resp=resp)
        # Get new commands.
        self.commands.extend(self._get_commands(resp=resp))

    def reset(self) -> None:
        self.cached_static_data = False

    @abstractmethod
    def _cache_static_data(self, resp: List[bytes]) -> None:
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
        raise Exception()
