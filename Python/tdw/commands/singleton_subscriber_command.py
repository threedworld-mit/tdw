# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.command import Command


class SingletonSubscriberCommand(Command, ABC):
    """
    These commands act as singletons and can subscribe to events.
    """

    def __init__(self):
        """
        (no arguments)
        """

        super().__init__()