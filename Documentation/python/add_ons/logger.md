# Logger

`from tdw.add_ons.logger import Logger`

Log every command sent to the build.

```python
from tdw.controller import Controller
from tdw.add_ons.logger import Logger

c = Controller()
logger = Logger(path="log.txt")
c.add_ons.append(logger)
# The logger add-on will log this command.
c.communicate({"$type": "do_nothing"})
c.communicate({"$type": "terminate"})
```

The log file can be automatically re-loaded into another controller using the [`LogPlayback`](log_playback.md) add-on.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Logger(path)`**

**`Logger(path, overwrite=True, log_commands_in_build=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  PATH |  | The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| overwrite |  bool  | True | If True and a log file already exists at `path`, overwrite the file. |
| log_commands_in_build |  bool  | False | If True, the build will log every message received and every command executed in the [Player log](https://docs.unity3d.com/Manual/LogFiles.html). |

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

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### reset

**`self.reset(path)`**

**`self.reset(path, overwrite=True)`**

Reset the logger.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  PATH |  | The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| overwrite |  bool  | True | If True and a log file already exists at `path`, overwrite the file. |