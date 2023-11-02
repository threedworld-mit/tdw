from typing import Dict, List, Tuple
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.ui import UI


class ProgressBar(UI):
    """
    Two rectangles used to display a value between 0 and 1, which can be set or incremented/decremented.

    This is a subclass of `UI` but can coincide with any other `UI` add-on or subclass thereof.

    You don't need to set a unique `canvas_id`: this `ProgressBar` will automatically use a canvas with that ID if one already exists.
    """

    def __init__(self, value: float = 0, increment: bool = True, left_to_right: bool = True, size: Dict[str, int] = None,
                 overlay_color: Dict[str, float] = None, underlay_color: Dict[str, float] = None,
                 anchor: Dict[str, float] = None, pivot: Dict[str, float] = None, position: Dict[str, int] = None,
                 canvas_id: int = 0):
        """
        :param value: The initial value as a fraction of the total time (0 to 1).
        :param increment: If True, the progress bar is incrementing. If False, the progress bar is decrementing. This determines whether the progress bar is done when its value is 0 or 1.
        :param left_to_right: If true, the progress bar increments leftwards.
        :param size: The size of the progress bar in pixels.
        :param underlay_color: The color of the progress bar underlay.
        :param overlay_color: The color of the progress bar overlay.
        :param anchor: The anchor of the progress bar. If this is (1, 1), then position (0, 0) is the top-right of the screen.
        :param pivot: The pivot of the progress bar. If this is (1, 1), then the pivot is the bar's top-right corner.
        :param position: The anchor position of the UI element in pixels. x is lateral, y is vertical. The anchor position is not the true pixel position. For example, if the anchor is {"x": 0, "y": 0} and the position is {"x": 0, "y": 0}, the UI element will be in the bottom-left of the screen.
        :param canvas_id: The ID of the canvas.
        """

        super().__init__(canvas_id=canvas_id)
        """:field
        If True, the progress bar is at its final value (1 if incrementing, 0 if decrementing).
        """
        self.done: bool = False
        self._value: float = value
        self._increment: bool = increment
        self._left_to_right: bool = left_to_right
        if size is None:
            self._size: Dict[str, int] = {"x": 400, "y": 24}
        else:
            self._size: Dict[str, int] = size
        if underlay_color is None:
            self._underlay_color: Tuple[int, int, int] = (0, 0, 0)
        else:
            self._underlay_color = tuple(TDWUtils.color_to_array(underlay_color)[:-1])
        if overlay_color is None:
            self._overlay_color: Tuple[int, int, int] = (255, 255, 255)
        else:
            self._overlay_color = tuple(TDWUtils.color_to_array(overlay_color)[:-1])
        if anchor is None:
            self._anchor: Dict[str, float] = {"x": 1, "y": 1}
        else:
            self._anchor = anchor
        if pivot is None:
            self._pivot: Dict[str, float] = {"x": 1, "y": 1}
        else:
            self._pivot = pivot
        if position is None:
            self._position: Dict[str, int] = {"x": 0, "y": 0}
        else:
            self._position = position
        # This will be set during initialization.
        self._overlay_id: int = 0

    def get_initialization_commands(self) -> List[dict]:
        # Initialization the UI.
        commands = super().get_initialization_commands()
        # Add the underlay image.
        self.add_image(image=self._get_image(self._underlay_color, size=self._size), position=self._position,
                       size=self._size, rgba=False, anchor=self._anchor, pivot=self._pivot, raycast_target=False)
        # Set the pivot and position depending on the direction of the progress bar.
        overlay_pivot = {"x": 0, "y": self._pivot["y"]} if self._left_to_right else self._pivot
        overlay_position = {"x": self._position["x"] - self._size["x"],
                            "y": self._position["y"]} if self._left_to_right else self._position
        # Add the overlay image.
        self._overlay_id = self.add_image(image=self._get_image(self._overlay_color, size=self._size),
                                          position=overlay_position, size=self._size, rgba=False, anchor=self._anchor,
                                          pivot=overlay_pivot, raycast_target=False)
        # Resize the overlay image.
        self._set_overlay_size()
        # Append the commands that just created those images and return.
        commands.extend(self.commands[:])
        self.commands.clear()
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        # Set the progress bar's size.
        self._set_overlay_size()

    def set_value(self, value: float) -> None:
        """
        Set the internal progress bar value.

        :param value: The new value. This will be clamped to be between 0 and 1.
        """

        self._value = max(0.0, min(value, 1.0))

    def increment_value(self, delta: float) -> None:
        """
        Increment or decrement the progress bar.

        :param delta: Increment or decrement by this delta value (-1 to 1).
        """

        self._value = max(0.0, min(self._value + delta, 1.0))
        self.done = (self._value >= 1 and self._increment) or (self._value <= 0 and not self._increment)

    def _set_overlay_size(self) -> None:
        """
        Set the size of the overlay rectangle based on the progress bar value.
        """

        self.set_size(ui_id=self._overlay_id, size={"x": int(self._size["x"] * self._value), "y": self._size["y"]})
