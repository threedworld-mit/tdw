from typing import List, Generic
from abc import ABC, abstractmethod
from tdw.add_ons.agent.id_var import T


class AgentState(ABC, Generic[T]):
    def __init__(self, agent_id: T, resp: List[bytes]):
        self.id: T = agent_id
        self._set_state(resp=resp)

    @abstractmethod
    def _set_state(self, resp: List[bytes]) -> None:
        raise Exception()
