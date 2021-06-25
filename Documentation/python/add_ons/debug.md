# Debug

`from tdw.add_ons.debug import Debug`

Use this module to record and playback every command sent to the build.

```python
from tdw.controller import Controller
from tdw.add_ons.debug import Debug

c = Controller(launch_build=False)
d = Debug(record=True, path="log.json")
c.add_ons.append(d)
# The debug add-on will log this command.
c.communicate({"$type": "do_nothing"})
# The debug add-on will log this command and generate a log.json file.
c.communicate({"$type": "terminate"})
```

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `record` If True, record each command. If False, play back an existing record.

- `playback` A record of each list of commands sent to the build.

***

## Functions

#### \_\_init\_\_

**`Debug(record, path)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record |  bool |  | If True, record each command. If False, play back an existing record. |
| path |  Union[str, Path] |  | The path to either save the record to or load the record from. |

#### on_communicate

**`self.on_communicate(resp)`**

This is called after commands are sent to the build and a response is received.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### previous_commands

**`self.previous_commands(commands)`**

Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that were just sent to the build. |

### save

**`self.save()`**

Write the record of commands sent to the local disk.

