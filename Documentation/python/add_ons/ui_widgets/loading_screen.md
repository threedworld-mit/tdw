# LoadingScreen

`from tdw.add_ons.ui_widgets.loading_screen import LoadingScreen`

Add a loading screen. For this to work correctly, it should always be the *last* element of `c.add_ons`.
The loading screen will always appear before anything else.
But if the add-on is last in `c.add_ons` it will be removed after all other initialization commands.

***

## Functions

#### \_\_init\_\_

**`LoadingScreen()`**

**`LoadingScreen(canvas_id=0, text="Loading...", text_size=64)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| canvas_id |  int  | 0 | The ID of the UI canvas. |
| text |  str  | "Loading..." | The loading message text. |
| text_size |  int  | 64 | The font size of the loading message text. |