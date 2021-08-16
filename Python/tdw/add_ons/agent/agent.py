from typing import List, TypeVar, Generic, Optional
from abc import ABC, abstractmethod
from overrides import final
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.agent.agent_state import AgentState
from tdw.add_ons.agent_manager import AgentManager
from tdw.add_ons.agent.id_var import T


U = TypeVar("U", bound=AgentState)
V = TypeVar("V", bound=AgentState)
W = TypeVar("W", bound=AgentManager)


class Agent(AddOn, ABC, Generic[T, U, V]):
    def __init__(self, agent_id: T):
        super().__init__()
        self.id: T = agent_id
        self.static: Optional[U] = None
        self.dynamic: Optional[V] = None

    @abstractmethod
    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per agent.

        :return: A list of commands that will initialize this agent.
        """

        raise Exception()

    @final
    def step(self, resp: List[bytes], agent_manager: W) -> List[dict]:
        # Set the static state.
        if self.static is None:
            self.static: U = self._get_static(resp=resp, agent_manager=agent_manager)
        # Update the dynamic state.
        self.dynamic: V = self._get_dynamic(resp=resp, agent_manager=agent_manager)
        return self._get_commands(resp=resp, agent_manager=agent_manager)

    @abstractmethod
    def _get_static(self, resp: List[bytes], agent_manager: W) -> U:
        raise Exception()

    @abstractmethod
    def _get_dynamic(self, resp: List[bytes], agent_manager: W) -> V:
        """
        :param resp: The response from the build.

        :return: The updated agent state.
        """

        raise Exception()

    def _get_commands(self, resp: List[bytes], agent_manager: W) -> List[dict]:
        raise Exception()
