from typing import List, Dict
from abc import ABC, abstractmethod
import numpy as np
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian


class ProcGenObject(ABC):
    if "models_core.json" not in Controller.MODEL_LIBRARIANS:
        Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")

    def __init__(self, position: Dict[str, float], north_south: bool):
        self.position: Dict[str, float] = position
        self.north_south: bool = north_south

    @abstractmethod
    def create(self, rng: np.random.RandomState) -> List[dict]:
        raise Exception()