##### Write Data

# The `JsonWriter` add-on

It is often very easy to serialize TDW data into a JSON dictionary (for more explanation, [read this](custom_writers.md)). TDW includes the option to serialize arbitrary data objects to JSON files by adding the [`JsonWriter`](../../python/add_ons/json_writer.md) add-on to a controller:

```python
import json
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.json_writer import JsonWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("encode_json")
if not output_directory.exists():
    output_directory.mkdir(parents=True)
print(f"Data will be saved to: {output_directory}")
c = Controller()
# Add a robot.
robot = Robot(name="ur5")
# Add a JSON writer.
writer = JsonWriter(objects={"robot": robot}, output_directory=output_directory, include_hidden_fields=False, indent=2, zero_padding=8)
c.add_ons.extend([robot, writer])
# Create the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
# End the simulation.
c.communicate({"$type": "terminate"})
```

## The `objects` parameter

The `objects` parameter refers not to [TDW objects](../core_concepts/objects.md) but Python data objects such as a `Robot` add-on or a Python dictionary. These are the objects are serialized to JSON files per-frame. `objects` is a dictionary where the key is a name or identifier; this is used to create the filename.

## The `output_directory` parameter

This sets the output directory. Every object in `objects` is written to this directory per frame.

Example writer:

```
writer = JsonWriter(objects={"robot": robot, "object_manager": object_manager}, output_directory="output")
```

Example output after running a controller for 3 frames:

```
output/
....robot_00000000.json
....robot_00000001.json
....robot_00000002.json
....object_manager_00000000.json
....object_manager_00000001.json
....object_manager_00000002.json
```

## The `include_hidden_fields` parameter

`include_hidden_fields` is an optional parameter. Many data classes in TDW use hidden fields that have names beginning with `_` that aren't included in the documentation; they tend to store internal data that users aren't meant to directly access.

By default, `include_hidden_fields` is set to False. Many TDW data classes hold a *lot* of data in hidden fields and serializing all of it will noticeably slow your simulation. By setting `include_hidden_fields` to False you will often exclude a lot of extraneous data.

## Read and deserialize saved data

Deserialize data by calling `read(path)` or `read(value)`:

```python
import json
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.json_writer import JsonWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("encode_json")
if not output_directory.exists():
    output_directory.mkdir(parents=True)
print(f"Data will be saved to: {output_directory}")
c = Controller()
# Add a robot.
robot = Robot(name="ur5")
# Add a JSON writer.
writer = JsonWriter(objects={"robot": robot}, output_directory=output_directory, include_hidden_fields=False, indent=2, zero_padding=8)
c.add_ons.extend([robot, writer])
# Create the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
# End the simulation.
c.communicate({"$type": "terminate"})
# Print the JSON dictionary.
path = output_directory.joinpath("robot_00000000.json")
print(writer.read(path))
```

The `path` parameter can be a string (a file path), a [`Path`](https://docs.python.org/3/library/pathlib.html) (also a file path), or an integer representing the frame count. If `path` is an integer, then `read()` will return a *dictionary of dictionaries* where the key is the name of the object, and the value is the deserialized data. 

In this example, we'll create a simple [multi-agent simulation](../multi_agent/overview.md) and request data for both agents:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.json_writer import JsonWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_agent_json")
c = Controller()
# Add two agents.
robot_0 = Robot(name="ur5",
                robot_id=0,
                position={"x": 3, "y": 0, "z": 1})
robot_1 = Robot(name="ur5", robot_id=1)
# Add a JSON writer. Write data for both agents.
writer = JsonWriter(objects={"robot_0": robot_0,
                             "robot_1": robot_1},
                    output_directory=output_directory)
c.add_ons.extend([robot_0, robot_1, writer])
# Load an empty scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
c.communicate({"$type": "terminate"})
print(writer.read(0))
```

Output (truncated for brevity):

```
{"robot_0": <data>, "robot_1": <data>}
```

## Reset `JsonWriter`

To reset `JsonWriter`, call `self.reset()`. To reset the output directory, set `self.output_directory` (note that this is a [`Path`](https://docs.python.org/3/library/pathlib.html)).

## The `Encoder` class

`JsonWriter` automatically writes data per-frame, which you might not always want to do. To manually encode data to a JSON dictionary, use TDW's custom JSON encoder:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.backend.encoder import Encoder

encoder = Encoder()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("encode_json")
if not output_directory.exists():
    output_directory.mkdir(parents=True)
print(f"Data will be saved to: {output_directory}")
c = Controller()
# Add a robot.
robot = Robot(name="ur5")
c.add_ons.extend([robot])
# Create the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
# Encode the robot to a JSON dictionary.
data = encoder.encode(robot)
print(data)
# End the simulation.
c.communicate({"$type": "terminate"})
```

## When to use `JsonWriter`

`JsonWriter` is useful if you want to dump arbitrary data to disk without having to know the Python class's internal structure. This is potentially useful for [multi-agent simulations](../multi_agent/overview.md) in which you may want to write each agent's data per frame without having to write a [custom writer](custom_writers.md) for each agent type.

## When to *not* use `JsonWriter`

- `JsonWriter` is the most general solution available in TDW for writing JSON data but it is by no means the best or most efficient. In many cases, you will want to write your own custom JSON writer. [Read this for more information.](custom_writers.md)
- **You can't automatically deserialize data written by `JsonWriter`.** If your goal is to recreate TDW data classes exactly as-is, you will need to write a custom deserializer. In many cases, TDW data class constructors aren't set up for this; this is a limitation of Python, which (at least in Python 3.6 and 3.7) disallows method overloading.

***

**Next: [The `OutputDataWriter` add-on](output_data_writer.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [write_json.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/write_data/write_json.py) Write TDW data class objects as JSON data and then read them.
- [write_multi_agent_json.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/write_data/write_multi_agent_json.py) An example of multi-agent JSON serialization.

Python API:

- [`JsonWriter`](../../python/add_ons/json_writer.md)