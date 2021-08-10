from typing import List, TypeVar, Generic, Optional
from abc import ABC, abstractmethod
from overrides import final
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.agent.agent_state import AgentState
from tdw.add_ons.agent.id_var import T


U = TypeVar("U", bound=AgentState)
V = TypeVar("V", bound=AgentState)


class Agent(AddOn, ABC, Generic[T, U, V]):
    def __init__(self, agent_id: T):
        super().__init__()
        self.id: T = agent_id
        self.static: Optional[U] = None
        self.dynamic: Optional[V] = None

    @final
    def on_send(self, resp: List[bytes]) -> None:
        # Set the static state.
        if self.static is None:
            self.static: U = self._get_static(resp=resp)
        # Update the dynamic state.
        self.dynamic: V = self._get_dynamic(resp=resp)

    @abstractmethod
    def _get_static(self, resp: List[bytes]) -> U:
        raise Exception()

    @abstractmethod
    def _get_dynamic(self, resp: List[bytes]) -> V:
        """
        :param resp: The response from the build.

        :return: The updated agent state.
        """

        raise Exception()
