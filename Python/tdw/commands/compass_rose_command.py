# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.command import Command


class CompassRoseCommand(Command, ABC):
    """
    These commands add or remove a non-physical compass rose to the scene.
    """

    def __init__(self):
        """
        (no arguments)
        """

        super().__init__()