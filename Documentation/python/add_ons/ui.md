# UI

`from tdw.add_ons.ui import UI`

Manager add-on for UI in TDW.

## Parameter types

All parameters of type `Dict[str, float]` are Vector2, e.g. `{"x": 0, "y": 0}`. There is no `"z"` parameter.

`"x"` is the horizontal value and `"y"` is the vertical value.

In some cases, this document will note that Vector2 values must be integers. This is usually because they are adjusting a value that references the actual screen pixels.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`UI()`**

**`UI(canvas_id=0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| canvas_id |  int  | 0 | The ID of the UI canvas. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### add_text

**`self.add_text(text, font_size, position)`**

**`self.add_text(text, font_size, position, anchor=None, pivot=None, color=None)`**

Add UI text to the scene.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| text |  str |  | The text. |
| font_size |  int |  | The size of the font. |
| position |  Dict[str, int] |  | The screen (pixel) position as a Vector2. Values must be integers. |
| anchor |  Dict[str, float] | None | The anchor as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`. |
| pivot |  Dict[str, float] | None | The pivot as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`. |
| color |  Dict[str, float] | None | The color of the text. If None, defaults to `{"r": 1, "g": 1, "b": 1, "a": 1}`. |

_Returns:_  The ID of the new UI element.

#### add_image

**`self.add_image(image, position, size)`**

**`self.add_image(image, position, size, rgba=True, scale_factor=None, anchor=None, pivot=None, color=None)`**

Add a UI image to the scene.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| image |  Union[str, Path, bytes] |  | The image. If a string or `Path`, this is a filepath. If `bytes`, this is the image byte data. |
| position |  Dict[str, int] |  | The screen (pixel) position as a Vector2. Values must be integers. |
| size |  Dict[str, int] |  | The pixel size of the image as a Vector2. Values must be integers and must match the actual image size. |
| rgba |  bool  | True | If True, this is an RGBA image. If False, this is an RGB image. |
| scale_factor |  Dict[str, float] | None | Scale the UI image by this factor. If None, defaults to {"x": 1, "y": 1}. |
| anchor |  Dict[str, float] | None | The anchor as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`. |
| pivot |  Dict[str, float] | None | The pivot as a Vector2. Values are floats between 0 and 1. If None, defaults to `{"x": 0.5, "y": 0.5}`. |
| color |  Dict[str, float] | None | The color of the text. If None, defaults to `{"r": 1, "g": 1, "b": 1, "a": 1}`. |

_Returns:_  The ID of the new UI element.

#### set_text

**`self.set_text(ui_id, text)`**

Set the text of a UI text element that is already in the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| ui_id |  int |  | The ID of the UI text element. |
| text |  str |  | The text. |

#### set_size

**`self.set_size(ui_id, size)`**

Set the size of a UI element that is already in the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| ui_id |  int |  | The ID of the UI element. |
| size |  Dict[str, float] |  | The size. |

#### attach_canvas_to_avatar

**`self.attach_canvas_to_avatar()`**

**`self.attach_canvas_to_avatar(avatar_id="a", focus_distance=2.5, plane_distance=0.101)`**

Attach the UI canvas to an avatar. This allows the UI to appear in image output data.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | "a" | The avatar ID. |
| focus_distance |  float  | 2.5 | The focus distance. If the focus distance is less than the default value (2.5), the UI will appear blurry unless post-processing is disabled. |
| plane_distance |  float  | 0.101 | The distance from the camera to the UI canvas. This should be slightly further than the near clipping plane. |

#### attach_canvas_to_vr_rig

**`self.attach_canvas_to_vr_rig()`**

**`self.attach_canvas_to_vr_rig(plane_distance=0.25)`**

Attach the UI canvas to a VR rig.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| plane_distance |  float  | 0.25 | The distance from the camera to the UI canvas. |

#### destroy

**`self.destroy(ui_id)`**

Destroy a UI element.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| ui_id |  int |  | The ID of the UI element. |

#### destroy_all

**`self.destroy_all()`**

**`self.destroy_all(destroy_canvas=False)`**

Destroy all UI elements.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| destroy_canvas |  bool  | False | If True, destroy the UI canvas and all of its UI elements. If False, destroy the canvas' UI elements but not the canvas itself. |

#### add_loading_screen

**`self.add_loading_screen()`**

**`self.add_loading_screen(text="Loading...", text_size=64)`**

A macro for adding a simple load screen. Combines `self.add_image()` (adds a black background) and `self.add_text()` (adds a loading message).


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| text |  str  | "Loading..." | The loading message text. |
| text_size |  int  | 64 | The font size of the loading message text. |

_Returns:_  Tuple: The ID of the background image, the ID of the text.