# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.ui_element_command import UiElementCommand
from typing import Dict


class AddUiCommand(UiElementCommand, ABC):
    """
    These commands add UI elements to the scene.
    """

    def __init__(self, id: int, anchor: Dict[str, float] = None, pivot: Dict[str, float] = None, position: Dict[str, int] = None, color: Dict[str, float] = None, raycast_target: bool = True, canvas_id: int = 0):
        """
        :param id: The unique ID of the UI element.
        :param anchor: The anchor of the UI element. The values must be from 0 (left or bottom) to 1 (right or top). By default, the anchor is in the center.
        :param pivot: The pivot of the UI element. The values must be from 0 (left or bottom) to 1 (right or top). By default, the pivot is in the center.
        :param position: The anchor position of the UI element in pixels. x is lateral, y is vertical. The anchor position is not the true pixel position. For example, if the anchor is {"x": 0, "y": 0} and the position is {"x": 0, "y": 0}, the UI element will be in the bottom-left of the screen.
        :param color: The color of the UI element.
        :param raycast_target: If True, raycasts will hit the UI element.
        :param canvas_id: The unique ID of the UI canvas.
        """

        super().__init__(id=id, canvas_id=canvas_id)
        if anchor is None:
            """:field
            The anchor of the UI element. The values must be from 0 (left or bottom) to 1 (right or top). By default, the anchor is in the center.
            """
            self.anchor: Dict[str, float] = {"x": 0.5, "y": 0.5}
        else:
            self.anchor = anchor
        if pivot is None:
            """:field
            The pivot of the UI element. The values must be from 0 (left or bottom) to 1 (right or top). By default, the pivot is in the center.
            """
            self.pivot: Dict[str, float] = {"x": 0.5, "y": 0.5}
        else:
            self.pivot = pivot
        if position is None:
            """:field
            The anchor position of the UI element in pixels. x is lateral, y is vertical. The anchor position is not the true pixel position. For example, if the anchor is {"x": 0, "y": 0} and the position is {"x": 0, "y": 0}, the UI element will be in the bottom-left of the screen.
            """
            self.position: Dict[str, int] = {"x": 0, "y": 0}
        else:
            self.position = position
        if color is None:
            """:field
            The color of the UI element.
            """
            self.color: Dict[str, float] = {"r": 1, "g": 1, "b": 1, "a": 1}
        else:
            self.color = color
        """:field
        If True, raycasts will hit the UI element.
        """
        self.raycast_target: bool = raycast_target
