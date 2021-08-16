from typing import List
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.agent.agent import Agent


class AgentManager(AddOn):
    def __init__(self):
        super().__init__()
        self.agents: List[Agent] = list()
        self.__cached_static_data: bool = False

    def get_initialization_commands(self) -> List[dict]:
        commands = []
        for agent in self.agents:
            commands.extend(agent.get_initialization_commands())
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        for agent in self.agents:
            self.commands.extend(agent.step(resp=resp, agent_manager=self))
