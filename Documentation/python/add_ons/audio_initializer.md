# AudioInitializer

`from tdw.add_ons.audio_initializer import AudioInitializer`

Initialize standard (Unity) audio.

This assumes that an avatar corresponding to `avatar_id` has already been added to the scene.

***

## Fields

- `avatar_id` The ID of the listening avatar.

***

## Functions

#### \_\_init\_\_

**`AudioInitializer()`**

**`AudioInitializer(avatar_id="a", framerate=60)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_id |  str  | "a" | The ID of the listening avatar. |
| framerate |  int  | 60 | The target simulation framerate. |

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



