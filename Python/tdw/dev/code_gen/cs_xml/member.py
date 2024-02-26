from abc import ABC, abstractmethod
from inflection import  underscore


class Member(ABC):
    """
    A member of a namespace: An enum, class, or struct.
    """

    def __init__(self, name: str, description: str, namespace: str):
        """
        :param name: The name of the member.
        :param description: A description of the member.
        :param namespace: The member's C# namespace.
        """

        """:field
        The name of the member.
        """
        self.name: str = name
        """:field
        A description of the member.
        """
        self.description: str = description
        """:field
        The member's C# namespace.
        """
        self.namespace: str = namespace
        """:field
        The member's import path, if it were a Python class.
        """
        self.import_path: str = ".".join([underscore(n) for n in namespace.split("::")]).replace("web_gl", "webgl")
        if self.import_path == "tdw_input":
            self.import_path = self._get_tdwinput_import_path()

    @abstractmethod
    def _get_tdwinput_import_path(self) -> str:
        """
        :return: The import path if the C# namespace is TDWInput.
        """

        raise Exception()
