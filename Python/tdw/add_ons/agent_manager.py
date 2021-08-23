from typing import List
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.agents.agent import Agent


class AgentManager(AddOn):
    """
    A manager class for multi-agent simulations.
    """

    def __init__(self):
        super().__init__()
        """:field
        A list of all of this manager's agents. You must add every agent when the AgentManager is first initialized, otherwise they might not appear correctly in the output data.
        """
        self.agents: List[Agent] = list()

    def get_initialization_commands(self) -> List[dict]:
        commands = []
        # Initialize the agents.
        for agent in self.agents:
            commands.extend(agent.get_initialization_commands())
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Append the agent commands.
        for agent in self.agents:
            agent.step(resp=resp)
            self.commands.extend(agent.commands)

    def reset(self) -> None:
        # Reset all agent data.
        for agent in self.agents:
            agent.reset()
        self.initialized = False
