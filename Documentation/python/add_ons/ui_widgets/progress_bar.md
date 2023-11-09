# ProgressBar

`from tdw.add_ons.ui_widgets.progress_bar import ProgressBar`

Two rectangles used to display a value between 0 and 1, which can be set or incremented/decremented.

This is a subclass of `UI` but can coincide with any other `UI` add-on or subclass thereof.

You don't need to set a unique `canvas_id`: this `ProgressBar` will automatically use a canvas with that ID if one already exists.

***

## Fields

- `done` If True, the progress bar is at its final value (1 if incrementing, 0 if decrementing).

***

## Functions

#### \_\_init\_\_

**`ProgressBar()`**

**`ProgressBar(value=0, increment=True, left_to_right=True, size=None, underlay_color=None, overlay_color=None, anchor=None, pivot=None, position=None, canvas_id=0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| value |  float  | 0 | The initial value as a fraction of the total time (0 to 1). |
| increment |  bool  | True | If True, the progress bar is incrementing. If False, the progress bar is decrementing. This determines whether the progress bar is done when its value is 0 or 1. |
| left_to_right |  bool  | True | If true, the progress bar increments leftwards. |
| size |  Dict[str, int] | None | The size of the progress bar in pixels. |
| underlay_color |  Dict[str, float] | None | The color of the progress bar underlay. |
| overlay_color |  Dict[str, float] | None | The color of the progress bar overlay. |
| anchor |  Dict[str, float] | None | The anchor of the progress bar. If this is (1, 1), then position (0, 0) is the top-right of the screen. |
| pivot |  Dict[str, float] | None | The pivot of the progress bar. If this is (1, 1), then the pivot is the bar's top-right corner. |
| position |  Dict[str, int] | None | The anchor position of the UI element in pixels. x is lateral, y is vertical. The anchor position is not the true pixel position. For example, if the anchor is {"x": 0, "y": 0} and the position is {"x": 0, "y": 0}, the UI element will be in the bottom-left of the screen. |
| canvas_id |  int  | 0 | The ID of the canvas. |

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