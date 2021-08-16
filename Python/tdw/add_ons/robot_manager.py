from typing import List, Dict
from tdw.output_data import OutputData, Transforms, Bounds, Rigidbodies
from tdw.add_ons.agent_manager import AgentManager


class RobotManager(AgentManager):
    def __init__(self):
        super().__init__()
        self.objects_static: Dict[int]