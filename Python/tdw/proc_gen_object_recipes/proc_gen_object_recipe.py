from typing import List, Dict
from abc import ABC, abstractmethod
import numpy as np
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian


class ProcGenObjectRecipe(ABC):
    """
    A recipe for procedurally generating a group of objects such as a table with chairs around it.

    These recipes have a "root" object that is usually kinematic.
    These root objects are assumed to be aligned north-south or east-west (0 or 90 degrees).
    """

    if "models_core.json" not in Controller.MODEL_LIBRARIANS:
        Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")

    def __init__(self, position: Dict[str, float], north_south: bool, rng: np.random.RandomState = None):
        """
        :param position: The position of the object.
        :param north_south: If True, the object is aligned north-south (0 degree rotation). If False, the object is aligned east-west (90 degree rotation).
        :param rng: The random number generator. If None, a generator is created.
        """

        """:field
        The position of the object.
        """
        self.position: Dict[str, float] = position
        """:field
        If True, the object is aligned north-south (0 degree rotation). If False, the object is aligned east-west (90 degree rotation).
        """
        self.north_south: bool = north_south
        if rng is None:
            self._rng: np.random.RandomState = np.random.RandomState()
        else:
            self._rng = rng

    @abstractmethod
    def create(self) -> List[dict]:
        """
        :return: A list of commands to create the objects.
        """

        raise Exception()
