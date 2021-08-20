from typing import List, Dict
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.manager import Manager
from tdw.add_ons.agents.agent import Agent


class AgentManager(AddOn):
    def __init__(self):
        super().__init__()
        """:field
        A dictionary of manager add-ons. Key = An identifier for the add-on. Agents can use this key to determine if the AgentManager has all of the add-ons that the agent needs.
        An agent can add to this when the manager is initialized.
        These add-ons will inject commands into `self.commands` in a fixed order. Then the agents will inject their commands.
        """
        self.managers: Dict[str, Manager] = dict()
        """:field
        A list of all of this manager's agents. You must add every agent when the AgentManager is first initialized, otherwise they might not appear correctly in the output data.
        """
        self.agents: List[Agent] = list()

    def get_initialization_commands(self) -> List[dict]:
        # Append required managers.
        for agent in self.agents:
            required_managers = agent.get_required_managers()
            for k in required_managers:
                if k not in self.managers:
                    self.managers[k] = required_managers[k]
        commands = []
        # Initialize all of my add-ons.
        for manager in self.managers.values():
            commands.extend(manager.get_initialization_commands())
            manager.initialized = True
        # Initialize the agents.
        for agent in self.agents:
            commands.extend(agent.get_initialization_commands())
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Append the add-on commands.
        for manager in self.managers.values():
            manager.on_send(resp=resp)
            self.commands.extend(manager.commands)
        # Append the agent commands.
        for agent in self.agents:
            agent.step(resp=resp)
            self.commands.extend(agent.commands)

    def reset(self) -> None:
        # Reset all manager data.
        for manager in self.managers.values():
            manager.reset()
        # Reset all agent data.
        agent_types: set = set()
        for agent in self.agents:
            if agent.__class__ not in agent_types:
                agent_types.add(agent.__class__)
                agent.reset()
