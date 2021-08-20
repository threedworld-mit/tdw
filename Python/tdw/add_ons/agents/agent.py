from typing import List, TypeVar, Generic, Optional
from abc import ABC, abstractmethod
from overrides import final
from tdw.add_ons.agent_manager import AgentManager
from tdw.add_ons.agents.agent_state import AgentState

T = TypeVar("T", bound=AgentState)
U = TypeVar("U", bound=AgentState)


class Agent(ABC, Generic[T, U]):
    def __init__(self):
        super().__init__()
        self.static: Optional[T] = None
        self.dynamic: Optional[U] = None
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
        # Set the static state.
        if self.static is None:
            self.static: T = self._get_static(resp=resp, agent_manager=agent_manager)
        # Update the dynamic state.
        self.dynamic: U = self._get_dynamic(resp=resp, agent_manager=agent_manager)
        self.commands.extend(self._get_commands(resp=resp, agent_manager=agent_manager))

    @abstractmethod
    def _get_static(self, resp: List[bytes], agent_manager: AgentManager) -> T:
        raise Exception()

    @abstractmethod
    def _get_dynamic(self, resp: List[bytes], agent_manager: AgentManager) -> U:
        """
        :param resp: The response from the build.

        :return: The updated agent state.
        """

        raise Exception()

    def _get_commands(self, resp: List[bytes], agent_manager: AgentManager) -> List[dict]:
        raise Exception()
