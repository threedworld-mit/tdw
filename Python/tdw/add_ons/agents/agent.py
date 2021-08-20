from typing import List
from abc import ABC, abstractmethod
from overrides import final
from tdw.add_ons.agent_manager import AgentManager


class Agent(ABC):
    def __init__(self):
        super().__init__()
        self._cached_static_data: bool = False
        self.commands: List[dict] = list()

    @abstractmethod
    def add_required_add_ons(self, agent_manager: AgentManager) -> None:
        raise Exception()

    @abstractmethod
    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per agent.

        :return: A list of commands that will initialize this agent.
        """

        raise Exception()

    @final
    def step(self, resp: List[bytes], agent_manager: AgentManager) -> None:
        # Cache the static state.
        if not self._cached_static_data:
            self._cached_static_data = True
            self._cache_static_data(resp=resp, agent_manager=agent_manager)
        # Update the dynamic state.
        self._set_dynamic_data(resp=resp, agent_manager=agent_manager)
        # Get new commands.
        self.commands.extend(self._get_commands(resp=resp, agent_manager=agent_manager))

    def reset(self) -> None:
        self._cached_static_data = False

    @abstractmethod
    def _cache_static_data(self, resp: List[bytes], agent_manager: AgentManager) -> None:
        raise Exception()

    @abstractmethod
    def _set_dynamic_data(self, resp: List[bytes], agent_manager: AgentManager) -> None:
        """
        :param resp: The response from the build.

        :return: The updated agent state.
        """

        raise Exception()

    def _get_commands(self, resp: List[bytes], agent_manager: AgentManager) -> List[dict]:
        raise Exception()
