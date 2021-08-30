from abc import ABC
from tdw.add_ons.add_on import AddOn


class Manager(AddOn, ABC):
    """
    Abstract class for a manager add-on. Manager add-ons have a state that can be reset.
    """

    def reset(self) -> None:
        self.initialized = False
