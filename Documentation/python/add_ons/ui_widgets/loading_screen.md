# LoadingScreen

`from tdw.add_ons.ui_widgets.loading_screen import LoadingScreen`

Add a loading screen. For this to work correctly, it should always be the *last* element of `c.add_ons`.
The loading screen will always appear before anything else.
But if the add-on is last in `c.add_ons` it will be removed after all other initialization commands.

***

## Functions

#### \_\_init\_\_

**`LoadingScreen()`**

**`LoadingScreen(canvas_id=0, loading_text="Loading...", loading_text_size=64, instructions_text=None, instructions_text_size=36)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| canvas_id |  int  | 0 | The ID of the UI canvas. |
| loading_text |  str  | "Loading..." | The loading message text. |
| loading_text_size |  int  | 64 | The font size of the loading message text. |
| instructions_text |  str  | None | The instructions text subtitle. Can be None. |
| instructions_text_size |  int  | 36 | The size of the instructions text (if there is any). |