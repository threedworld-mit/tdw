# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.set_ui_element_command import SetUiElementCommand
from typing import Dict


class SetUiElementSize(SetUiElementCommand):
    """
    Set the size of a UI element.
    """

    def __init__(self, id: int, size: Dict[str, int], canvas_id: int = 0):
        """
        :param id: The unique ID of the UI element.
        :param size: The pixel size of the UI element.
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(id=id, canvas_id=canvas_id)
        """:field
        The pixel size of the UI element.
        """
        self.size: Dict[str, int] = size
