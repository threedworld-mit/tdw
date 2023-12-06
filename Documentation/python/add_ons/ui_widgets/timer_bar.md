# TimerBar

`from tdw.add_ons.ui_widgets.timer_bar import TimerBar`

A progress bar that decrements over time.

The timer won't start until you call `start()`.

***

## Fields

- `started` If True, the timer has started.

- `done` If True, the progress bar is at its final value (1 if incrementing, 0 if decrementing).

***

## Functions

#### \_\_init\_\_

**`TimerBar(total_time)`**

**`TimerBar(total_time, left_to_right=True, size=None, underlay_color=None, overlay_color=None, anchor=None, pivot=None, position=None, canvas_id=0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| total_time |  float |  | The total time that elapses until the timer is done. |
| left_to_right |  bool  | True | If true, the progress bar increments leftwards. |
| size |  Dict[str, int] | None | The size of the progress bar in pixels. |
| underlay_color |  Dict[str, float] | None | The color of the progress bar underlay. |
| overlay_color |  Dict[str, float] | None | The color of the progress bar overlay. |
| anchor |  Dict[str, float] | None | The anchor of the progress bar. If this is (1, 1), then position (0, 0) is the top-right of the screen. |
| pivot |  Dict[str, float] | None | The pivot of the progress bar. If this is (1, 1), then the pivot is the bar's top-right corner. |
| position |  Dict[str, int] | None | The anchor position of the UI element in pixels. x is lateral, y is vertical. The anchor position is not the true pixel position. For example, if the anchor is {"x": 0, "y": 0} and the position is {"x": 0, "y": 0}, the UI element will be in the bottom-left of the screen. |
| canvas_id |  int  | 0 | The ID of the canvas. The canvas must already exist or be added on this frame. |

#### set_value

**`self.set_value(value)`**

Set the internal progress bar value.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| value |  float |  | The new value. This will be clamped to be between 0 and 1. |

#### increment_value

**`self.increment_value(delta)`**

Increment or decrement the progress bar.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| delta |  float |  | Increment or decrement by this delta value (-1 to 1). |

#### start

**`self.start()`**

Start the timer.