from abc import ABC, abstractmethod
from typing import List
from tdw.librarian import ModelRecord


class ModelTest(ABC):
    """
    Run a test on a model.
    """

    def __init__(self, record: ModelRecord):
        """
        :param record: The model record.
        """

        # The model record.
        self._record: ModelRecord = record
        """:field
        A list of report strings after running the test.
        """
        self.reports: List[str] = list()
        """:field
        If True, the test is done.
        """
        self.done: bool = False

    @abstractmethod
    def start(self) -> List[dict]:
        """
        :return: A list of commands to start the test.
        """

        raise Exception()

    @abstractmethod
    def on_send(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The response from the build.

        :return: A list of commands to continue or end the test.
        """

        raise Exception()
