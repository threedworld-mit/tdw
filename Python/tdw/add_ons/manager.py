from abc import ABC
from tdw.add_ons.add_on import AddOn


class Manager(AddOn, ABC):
    def reset(self) -> None:
        self.initialized = False
