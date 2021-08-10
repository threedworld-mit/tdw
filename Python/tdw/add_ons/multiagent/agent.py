from typing import List, TypeVar, Generic, Optional
from abc import ABC, abstractmethod
from overrides import final
from tdw.add_ons.multiagent.agent_state import AgentState
from tdw.add_ons.multiagent.id_var import U


T = TypeVar("T", bound=AgentState)


class Agent(ABC, Generic[T, U]):
    def __init__(self, agent_id: U):
        self.id: U = agent_id
        self.state: Optional[T] = None

    @final
    def step(self, resp: List[bytes]) -> List[dict]:
        """
        Update the agent, given the response from the build. Set the agent's state and return a list of commands.
        
        :param resp: The response from the build.

        :return: A list of commands to send to the build.
        """

        self.state = self._set_state(resp=resp)
        return self._get_commands(resp=resp)

    @abstractmethod
    def _set_state(self, resp: List[bytes]) -> T:
        """
        :param resp: The response from the build.

        :return: The updated agent state.
        """

        raise Exception()

    @abstractmethod
    def _get_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The response from the build.

        :return: A list of commands to send to the build.
        """

        raise Exception()
