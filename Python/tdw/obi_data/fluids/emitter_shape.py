from overrides import final
from abc import ABC, abstractmethod


class EmitterShape(ABC):
    """
    The shape of an Obi emitter.
    """

    @final
    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {"$type": self._get_type()}
        d.update(self._get_dict())
        return d

    @abstractmethod
    def _get_type(self) -> str:
        """
        :return: The type name.
        """

        raise Exception()

    @abstractmethod
    def _get_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        raise Exception()
