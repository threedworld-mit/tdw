# JsonWriter

`from tdw.add_ons.json_writer import JsonWriter`

Dump JSON data of objects per-frame. *Objects* in this case refers not to TDW objects but to Python objects, such as a [`Robot`](robot.md) add-on or an arbitrary dictionary of data.

Per frame, these objects will be read, encoded into Python dictionaries, and written out as serialized JSON data files.

The JSON files can be read and reloaded like any other file with JSON information. However, TDW does not provide a means of automatically converting serialized JSON data back into objects.

Data is converted to JSON-serializable format as follows:

- Numpy arrays are converted to Python lists.
- Numpy `RandomState` objects, which many TDW classes use, are not serialized and receive a null value.
- `bytes` and `bytearray` objects are converted into base64 strings.
- [`Path`](https://docs.python.org/3/library/pathlib.html) objects are converted into absolute filepath strings.
- Some classes, namely those in the `tdw.FBOutput` namespace, can't readily be serialized to a dictionary; their values are instead set to null.
- Enum values are converted to their string representation i.e. `value.name`.
- Dictionaries that have non-string keys have all of their keys converted into strings i.e. `str(key)`.

***

## Fields

- `objects` A dictionary of objects to serialize. Key = A name or identifier for the object, for example `"robot"`. Value = A data object, for example a [`Robot`](robot.md).

- `output_directory` The root output directory as a [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`JsonJsonWriter(objects, output_directory)`**

**`JsonJsonWriter(objects, output_directory, indent=2, include_hidden_fields=False, zero_padding=8)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| objects |  Dict[str, object] |  | A dictionary of objects to serialize. Key = A name or identifier for the object, for example `"robot"`. Value = A data object, for example a [`Robot`](robot.md). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this doesn't exist, it will be created. |
| indent |  int  | 2 | The indentation level of the output JSON strings. |
| include_hidden_fields |  bool  | False | If True, include hidden fields in the JSON data i.e. any fields which have names that begin with `_`. This will give you *all* of the data, but often you won't want this. Many TDW classes hold megabytes of data in hidden fields, which is trivial to do in memory but serializing this data can be very slow. |
| zero_padding |  int  | 8 | How many zeros to append to the file name. By default, the name of the file of the first frame will be `00000000.txt`. |

#### reset

**`self.reset()`**

This will reset the frame count.

#### read

**`self.read(path)`**

Read saved ouput data.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path, int] |  | The path to the frame file. This can be a string or [`Path`](https://docs.python.org/3/library/pathlib.html) file path or an integer. If this is an integer, it represents the frame number; the file is assumed to be in `self.output_directory`. |

_Returns:_  If `path` is a string or a `Path`, this will return a dictionary. If `path` is an integer, this will return a *dictionary of dictionaries* where the key is the object name (e.g. `"robot"`) and the value is the corresponding dictionary.

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