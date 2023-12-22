# Writer

`from tdw.add_ons.writer import Writer`

Abstract base class for per-frame data writers.

***

## Fields

- `output_directory` The root output directory as a [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Writer(output_directory)`**

**`Writer(output_directory, zero_padding=8)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| output_directory |  PATH |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created. |
| zero_padding |  int  | 8 | How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`. |

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

**`self.reset()`**

This will reset the frame count.

#### read

**`self.read(path)`**

Read saved ouput data.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path, int] |  | The path to the frame file. This can be a string or [`Path`](https://docs.python.org/3/library/pathlib.html) file path or an integer. If this is an integer, it represents the frame number; the file is assumed to be in `self.output_directory`. |

_Returns:_  Deserialized data.