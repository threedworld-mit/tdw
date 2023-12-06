from time import time
from typing import Dict, List
from tdw.add_ons.ui_widgets.progress_bar import ProgressBar


class TimerBar(ProgressBar):
    """
    A progress bar that decrements over time.

    The timer won't start until you call `start()`.
    """

    def __init__(self, total_time: float, left_to_right: bool = True, size: Dict[str, int] = None,
                 underlay_color: Dict[str, float] = None, overlay_color: Dict[str, float] = None,
                 anchor: Dict[str, float] = None, pivot: Dict[str, float] = None, position: Dict[str, int] = None,
                 canvas_id: int = 0):
        """
        :param total_time: The total time that elapses until the timer is done.
        :param left_to_right: If true, the progress bar increments leftwards.
        :param size: The size of the progress bar in pixels.
        :param underlay_color: The color of the progress bar underlay.
        :param overlay_color: The color of the progress bar overlay.
        :param anchor: The anchor of the progress bar. If this is (1, 1), then position (0, 0) is the top-right of the screen.
        :param pivot: The pivot of the progress bar. If this is (1, 1), then the pivot is the bar's top-right corner.
        :param position: The anchor position of the UI element in pixels. x is lateral, y is vertical. The anchor position is not the true pixel position. For example, if the anchor is {"x": 0, "y": 0} and the position is {"x": 0, "y": 0}, the UI element will be in the bottom-left of the screen.
        :param canvas_id: The ID of the canvas. The canvas must already exist or be added on this frame.
        """

        super().__init__(value=1, increment=False, left_to_right=left_to_right, size=size,
                         overlay_color=overlay_color, underlay_color=underlay_color, anchor=anchor, pivot=pivot,
                         position=position, canvas_id=canvas_id)
        self._total_time: float = total_time
        self._start_time: float = 0
        """:field
        If True, the timer has started.
        """
        self.started: bool = False

    def start(self) -> None:
        """
        Start the timer.
        """

        self.started = True
        self._start_time = time()

    def on_send(self, resp: List[bytes]) -> None:
        # Don't do anything until the timer has been started by calling `self.start()`.
        if not self.started:
            return
        # Get the elapsed time since start.
        dt = time() - self._start_time
        # If the elapsed time exceeds the total time, we're done.
        if dt >= self._total_time:
            self.done = True
        # Set the progress bar value.
        self._value = 1 - dt / self._total_time
        super().on_send(resp=resp)
