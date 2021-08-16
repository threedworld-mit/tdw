from abc import ABC, abstractmethod
from typing import List
from overrides import final
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.agent.agent import Agent


class AgentManager(AddOn, ABC):
    def __init__(self):
        super().__init__()
        self.agents: List[Agent] = list()
        self.__cached_static_data: bool = False

    def get_initialization_commands(self) -> List[dict]:
        commands = []
        for agent in self.agents:
            commands.extend(agent.get_initialization_commands())
        return commands

    @final
    def on_send(self, resp: List[bytes]) -> None:
        if not self.__cached_static_data:
            self._cache_static_data(resp=resp)
        self._set_dynamic_data(resp=resp)
        for agent in self.agents:
            self.commands.extend(agent.step(resp=resp, agent_manager=self))

    @abstractmethod
    def _cache_static_data(self, resp: List[bytes]) -> None:
        raise Exception()

    def _set_dynamic_data(self, resp: List[bytes]) -> None:
        raise Exception()
