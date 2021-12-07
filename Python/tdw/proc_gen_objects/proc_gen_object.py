from typing import List, Dict
from abc import ABC, abstractmethod
import numpy as np


class ProcGenObject(ABC):
    def __init__(self, position: Dict[str, float], north_south: bool):
        self.position: Dict[str, float] = position
        self.north_south: bool = north_south

    @abstractmethod
    def create(self, rng: np.random.RandomState) -> List[dict]:
        raise Exception()