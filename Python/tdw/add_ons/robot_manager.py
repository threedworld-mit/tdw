from typing import List
from tdw.add_ons.agent_manager import AgentManager
from tdw.add_ons.object_manager import ObjectManager


class RobotManager(AgentManager):
    def __init__(self):
        super().__init__()
        self.object_manager: ObjectManager = ObjectManager()

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.extend(self.object_manager.get_initialization_commands())
        self.object_manager.initialized = True
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Update the world state.
        self.object_manager.on_send(resp=resp)
        super().on_send(resp=resp)
