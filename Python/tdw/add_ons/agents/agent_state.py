from typing import List
from abc import ABC, abstractmethod


class AgentState(ABC):
    """
    A minimal abstract class for holding state information about an agent.
    """

    def __init__(self, resp: List[bytes]):
        """
        :param resp: The response from the build.
        """

        self._set_state(resp=resp)

    @abstractmethod
    def _set_state(self, resp: List[bytes]) -> None:
        """
        Update the state from output data.

        :param resp: The response from the build.
        """

        raise Exception()
