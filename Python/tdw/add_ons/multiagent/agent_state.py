from typing import List
from abc import ABC
from tdw.add_ons.multiagent.id_var import U


class AgentState(ABC):
    def __init__(self, agent_id: U, resp: List[bytes]):
        pass
