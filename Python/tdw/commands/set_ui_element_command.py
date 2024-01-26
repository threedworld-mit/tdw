# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.ui_element_command import UiElementCommand


class SetUiElementCommand(UiElementCommand, ABC):
    """
    These commands set parameters of a UI element in the scene.
    """

    def __init__(self, id: int, canvas_id: int = 0):
        """
        :param id: The unique ID of the UI element.
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(id=id, canvas_id=canvas_id)
