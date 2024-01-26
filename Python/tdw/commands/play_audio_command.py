# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.command import Command
from typing import Dict


class PlayAudioCommand(Command, ABC):
    """
    These commands create audio clips and play them.
    """

    def __init__(self, id: int, position: Dict[str, float] = None, loop: bool = False):
        """
        :param id: A unique ID for this audio source.
        :param position: The position of the audio source.
        :param loop: If True, play the audio in a continuous loop.
        """

        super().__init__()
        """:field
        A unique ID for this audio source.
        """
        self.id: int = id
        if position is None:
            """:field
            The position of the audio source.
            """
            self.position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.position = position
        """:field
        If True, play the audio in a continuous loop.
        """
        self.loop: bool = loop