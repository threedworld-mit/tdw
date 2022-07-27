##### Write Data

# The `OutputDataWriter` add-on

The [`OutputDataWriter`](../../python/add_ons/output_data_writer.md) add-on will write the raw list of bytes returned by the build to disk per-frame.

The raw response is usually written as `resp` in our example controllers:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      Controller.get_add_object(model_name="vase_02",
                                                object_id=0),
                      {"$type": "send_transforms",
                       "frequency": "once"}])
print(resp)
c.communicate({"$type": "terminate"})
```

Output:

```
[b'\x14\x00\x00\x00tran\x0c\x00\x14\x00\x04\x00\x08\x00\x0c\x00\x10\x00\x0c\x00\x00\x00D\x00\x00\x000\x00\x00\x00\x18\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\xc6a\xcd6GUJ\xb8\x00\x00\x80?\x04\x00\x00\x00aU\xca7A[M6\x81\xfd\x837\x00\x00\x80?\x03\x00\x00\x00\x00J\x995\x00_\xf49\xa8t\xac\xb6\x01\x00\x00\x00\x00\x00\x00\x00', b'\x00\x00\x00\x02']
```

If we add an `OutputDataWriter`, on every frame each `bytes` object in `resp` will be encoded to a base64 string, then the list will be serialized to a string using JSON, and then the string will be saved to a file:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("output_data_writer")
print(f"Output will be saved to: {output_directory}")
c = Controller()
writer = OutputDataWriter(output_directory=output_directory)
c.add_ons.append(writer)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="vase_02",
                                         object_id=0),
               {"$type": "send_transforms",
                "frequency": "once"}])
c.communicate({"$type": "terminate"})
# Open the file and read the text.
path = output_directory.joinpath("00000000.txt")
print(path.read_text())
```

Output:

```
["FAAAAHRyYW4MABQABAAIAAwAEAAMAAAARAAAADAAAAAYAAAABAAAAAMAAADGYc02R1VKuAAAgD8EAAAAYVXKN0FbTTaB/YM3AACAPwMAAAAASpk1AF/0Oah0rLYBAAAAAAAAAA==", "AAAAAg=="]
```

## Read and deserialize saved data

We can read deserialize this data using the `read(path)` function:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("output_data_writer")
print(f"Output will be saved to: {output_directory}")
c = Controller()
writer = OutputDataWriter(output_directory=output_directory)
c.add_ons.append(writer)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="vase_02",
                                         object_id=0),
               {"$type": "send_transforms",
                "frequency": "once"}])
c.communicate({"$type": "terminate"})
# Open the file and read the text.
path = output_directory.joinpath("00000000.txt")
data = writer.read(path)
print(data)
```

Output:

```
[b'\x14\x00\x00\x00tran\x0c\x00\x14\x00\x04\x00\x08\x00\x0c\x00\x10\x00\x0c\x00\x00\x00D\x00\x00\x000\x00\x00\x00\x18\x00\x00\x00\x04\x00\x00\x00\x03\x00\x00\x00\xc6a\xcd6GUJ\xb8\x00\x00\x80?\x04\x00\x00\x00aU\xca7A[M6\x81\xfd\x837\x00\x00\x80?\x03\x00\x00\x00\x00J\x995\x00_\xf49\xa8t\xac\xb6\x01\x00\x00\x00\x00\x00\x00\x00', b'\x00\x00\x00\x02']
```

This output matches the output of the first example, when we printed `resp`.

The `path` parameter can be a string (a file path), a [`Path`](https://docs.python.org/3/library/pathlib.html) (also a file path), or an integer representing the frame count:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("output_data_writer")
print(f"Output will be saved to: {output_directory}")
c = Controller()
writer = OutputDataWriter(output_directory=output_directory)
c.add_ons.append(writer)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="vase_02",
                                         object_id=0),
               {"$type": "send_transforms",
                "frequency": "once"}])
c.communicate({"$type": "terminate"})
# Corresponds to: 00000000.txt
data = writer.read(0)
print(data)
```

## When to use `OutputDataWriter`

`OutputDataWriter` is best used as a debugging tool. It was created to debug `JsonWriter` quickly and without a controller; in this case, a controller script wrote out some output data and then `JsonWriter` used that data to "reset" some add-ons repeatedly as part of a test.

## When to *not* use `OutputDataWriter`

- `OutputDataWriter` is usually not significantly faster than parsing the raw bytes into output data objects and then serializing those. This is because it encodes to base64 before writing. Especially in the case of [images](../core_concepts/images.md), `OutputDataWriter` is probably not what you want to use.
- `OutputDataWriter` can't be used to reset scene states. It *can* be used to "reset" add-ons like this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.output_data_writer import OutputDataWriter
from tdw.add_ons.object_manager import ObjectManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Write raw output data per frame from the build.
"""

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("resp_saver")
print(f"Output data will be saved to: {path}")
c = Controller()
# Add an ObjectManager, which will start requesting output data.
object_manager = ObjectManager()
# Add an OutputDataWriter.
writer = OutputDataWriter(output_directory=path)
c.add_ons.extend([object_manager, writer])
# Get an object ID
object_id = 0
# Load the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                  object_id=object_id,
                                                  position={"x": 0, "y": 5, "z": 0}))
# Frame 0: Send the commands.
c.communicate(commands)
# Print the position of the object.
print("Frame 0:", object_manager.transforms[object_id].position[1])
# Frame 1: End the simulation.
c.communicate({"$type": "terminate"})
# Print the position of the object.
print("Frame 1:", object_manager.transforms[object_id].position[1])
# Load the saved data.
print("Reading saved data...")
frame_0 = writer.read(0)
frame_1 = writer.read(1)
# Create a new ObjectManager and set `initialized` to True because we don't need to send initialization commands.
object_manager = ObjectManager()
object_manager.initialized = True
# Call `on_send(frame_0) to reproduce the data at frame 0.
object_manager.on_send(resp=frame_0)
# Print the position of the object.
print("Frame 0:", object_manager.transforms[object_id].position[1])
# Call `on_send(frame_1) to reproduce the data at frame 1.
object_manager.on_send(resp=frame_1)
# Print the position of the object.
print("Frame 1:", object_manager.transforms[object_id].position[1])
```

Output:

```
Frame 0: 4.999019
Frame 1: 4.997057
Reading saved data...
Frame 0: 4.999019
Frame 1: 4.997057
```

While this can be useful (again, it's probably most useful as a debug tool), this doesn't actually set the positions and rotations of objects in the scene; it merely sets what the `ObjectManager` *thinks* the positions and rotations are.

***

**Next: [Create a custom data writer](custom_writers.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [write_output_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/write_data/write_output_data.py) Write raw output data per frame from the build.

Python API:

- [`OutputDataWriter`](../../python/add_ons/output_data_writer.md)
- [`ObjectManager`](../../python/add_ons/object_manager.md)