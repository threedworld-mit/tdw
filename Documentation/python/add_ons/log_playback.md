# LogPlayback

`from tdw.add_ons.log_playback import LogPlayback`

Load and play back commands that were logged by a [`Logger`](logger.md) add-on.

***

## Fields

- `playback` A list of lists of commands. Each list of commands is from a `communicate()` call from a prior controller, and will be sent per `communicate()` call to the current controller.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`LogPlayback()`**

A list of lists of commands. Each list of commands is from a `communicate()` call from a prior controller, and will be sent per `communicate()` call to the current controller.

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### load

**`self.load(path)`**

Load a log file. This will deserialize all of the commands in the log file and add each list of commands to `self.record`. Per `communicate()` call (i.e. when `on_send(resp)` is invoked), this add-on will pop the first list of commands and add it to `self.commands`; in other words, it will send each list of commands exactly as they were sent when they were logged.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path] |  | The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |