# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.ui_command import UiCommand


class UiElementCommand(UiCommand, ABC):
    """
    These commands add or adjust UI elements such as text or images.
    """

    def __init__(self, id: int, canvas_id: int = 0):
        """
        :param id: The unique ID of the UI element.
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(canvas_id=canvas_id)
        """:field
        The unique ID of the UI element.
        """
        self.id: int = id
