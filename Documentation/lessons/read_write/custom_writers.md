##### Read/Write to Disk

# Create a custom data writer

As noted elsewhere in this lesson, you will often want to write a custom data writer instead of, or in addition to, the writers that TDW already provides. Below are some tips for creating custom data writers:

## Custom JSON writers

JSON is one of the easiest serialization protocols to use, especially in Python. It's very easy to write custom JSON writers in your controller or in an add-on.

This example serializes data from an [`ObjectManager`](../../python/add_ons/object_manager.md). Note that we aren't serializing *everything*; this is intentional and part of the example. In this case, we assume that we want the position and rotation of each object but don't care about its forward directional vector, and that we need the model name and object ID but no other static data (such as segmentation color):

```python
import json
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class JsonWriterExample(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Add an object manager.
        self.object_manager = ObjectManager()
        self.add_ons.append(self.object_manager)

    def write_static(self, path: str) -> None:
        data = dict()
        for object_id in self.object_manager.objects_static:
            o = self.object_manager.objects_static[object_id]
            data[object_id] = {"name": o.name}
        with open(path, "wt") as f:
            f.write(json.dumps(data))

    def write_dynamic(self, path: str) -> None:
        data = dict()
        for object_id in self.object_manager.transforms:
            o = self.object_manager.transforms[object_id]
            data[object_id] = {"position": TDWUtils.array_to_vector3(o.position),
                               "rotation": TDWUtils.array_to_vector4(o.rotation)}
        with open(path, "wt") as f:
            f.write(json.dumps(data))


output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("custom_json")
print(f"Output will be saved to: {output_directory}")
if not output_directory.exists():
    output_directory.mkdir(parents=True)
c = JsonWriterExample()
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="vase_02",
                                         position={"x": 1, "y": 0, "z": -2},
                                         rotation={"x": 0, "y": 30, "z": 0},
                                         object_id=0)])
c.write_static(str(output_directory.joinpath("static.json").resolve()))
dynamic_path = str(output_directory.joinpath("dynamic.json").resolve())
c.write_dynamic(dynamic_path)
with open(dynamic_path, "rt") as f:
    print(f.read())
c.communicate({"$type": "terminate"})
```

Output:

```json
{"0": {"position": {"x": 0.9999985098838806, "y": 0.00046315044164657593, "z": -1.9999998807907104}, "rotation": {"x": -2.314517041668296e-05, "y": 0.25881654024124146, "z": 2.977321855723858e-05, "w": 0.9659265875816345}}}
```

## Improvement: Create a custom add-on

We can improve on this example. If we want to write dynamic data per frame, we could create a custom add-on that writes data within `self.on_send(resp)`. In this case, we'll create a subclass of `ObjectManager` so that we have easy access to all of its data:

```python
import json
from pathlib import Path
from typing import List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ObjectDataWriter(ObjectManager):
    """
    A custom sub-class of ObjectManager that writes the position and rotation of each object per frame.
    """
    
    def __init__(self, output_directory: Path, transforms: bool = True, rigidbodies: bool = False, bounds: bool = False):
        self.output_directory: Path = output_directory
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        self.frame: int = 0
        super().__init__(transforms=transforms, rigidbodies=rigidbodies, bounds=bounds)

    def on_send(self, resp: List[bytes]) -> None:
        # This calls ObjectManager.on_send(resp) to update the transforms of each object.
        super().on_send(resp=resp)
        # Write the data to a JSON file.
        data = dict()
        for object_id in self.transforms:
            o = self.transforms[object_id]
            data[object_id] = {"position": TDWUtils.array_to_vector3(o.position),
                               "rotation": TDWUtils.array_to_vector4(o.rotation)}
        # Get the file path.
        path = self.output_directory.joinpath(str(self.frame).zfill(4) + ".json")
        # Serialize the data and write it to the file.
        path.write_text(json.dumps(data))


if __name__ == "__main__":
    output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("custom_json")
    print(f"Output will be saved to: {output_directory}")
    c = Controller()
    writer = ObjectDataWriter(output_directory=output_directory)
    c.add_ons.append(writer)
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   Controller.get_add_object(model_name="vase_02",
                                             position={"x": 1, "y": 0, "z": -2},
                                             rotation={"x": 0, "y": 30, "z": 0},
                                             object_id=0)])
    dynamic_path = writer.output_directory.joinpath("0000.json")
    print(dynamic_path.read_text())
    c.communicate({"$type": "terminate"})
```

Output:

```json
{"0": {"position": {"x": 0.9999985098838806, "y": 0.00046315044164657593, "z": -1.9999998807907104}, "rotation": {"x": -2.314517041668296e-05, "y": 0.25881654024124146, "z": 2.977321855723858e-05, "w": 0.9659265875816345}}}
```

## Tips for JSON encoding

### 1. Cast from numpy data types to pure-Python data types

When encoding to JSON you may have errors about data types such as `int32` or `float32` not being serializable. This is because some of your data is using numpy data types; you must convert the data from numpy to pure-Python, like this:

```python
import numpy as np

arr = np.arange(0, 10)
json_arr = [float(v) for v in arr]
```

In the above example, we instead used `TDWUtils.array_to_vector3(arr)` and `TDWUtils.array_to_vector4(arr)` which automatically does the type cast for you and also converts the array into a dictionary:

```python
import numpy as np
from tdw.tdw_utils import TDWUtils

arr = np.array([0, 1, 2])
print(TDWUtils.array_to_vector3(arr))
```

Output:

```
{'x': 0.0, 'y': 1.0, 'z': 2.0}
```

### 2. Cast from enum types to string types

Many classes in TDW use enum values, which can't be serialized in JSON:

```python
from json import dumps
from tdw.robot_data.joint_type import JointType

v = JointType.revolute
print(dumps(v.name))
```

Output:

```
"revolute"
```

## Other types of output data writers

### 1. HDF5

HDF5 is a very good way to serialize relatively large datasets. [See the tdw_physics repo for an example.](https://github.com/alters-mit/tdw_physics/blob/master/tdw_physics/dataset.py)

**Advantages:**

- HDF5 is faster than JSON and the file size will be smaller. This is especially noticeable with large amounts of data.

**Disadvantages:**

- In general, it is much *easier* to write data using JSON than with HDF5. In cases where you only have small amounts of data, JSON is usually good enough.
- TDW doesn't include a pre-created HDF5 writer. The HDF5 format is very different from JSON in that there is no way to create a writer that will work in all cases while also utilizing HDF5's advantages in speed and file size.
- HDF5 works best when data is of uniform size. If you're trying to serialize arrays of different sizes per frame, HDF5 can be difficult and inefficient to use.
- HDF5 doesn't handle strings very well; it's best used for datasets that contain mostly numerical data.

### 2. SQL and SQLite

You can feasibly write TDW data to a SQL or SQLite database. At present, there are no examples of this.

**Advantages:**

- All of the usual advantages of using a database over saving files; you can create huge datasets that don't need to be loaded into memory all at once.

**Disadvantages:**

- This option is probably overkill in most cases. It requires a lot more effort than JSON or HDF5 to set up correctly.

### 3. XML

XML's advantages and disadvantages as a save file format are similar to JSON's. We recommend JSON over XML because there is less ambiguity in how and where data is serialized.

### 4. Pickle

Pickle is a Python-specific save file format. **We don't recommend using it.**

**Advantages:**

- It's very easy to code.

**Disadvantages:**

- Pickled data can include executable code, a major security problem.

### 5. Asynchronous threading

If you are writing lots of files, you can use threading to asynchronously save data. [See the tdw_image_dataset repo for an example.](https://github.com/alters-mit/tdw_image_dataset/blob/main/tdw_image_dataset/image_dataset.py)

**Advantages:**

- This can be noticeably faster than writing within a single thread. In the case of `tdw_image_dataset`, there is a pool of threads for asynchronously writing image data to disk.

**Disadvantages:**

- Threads are very hard to use correctly. You will have to deal with the usually problems with asynchronous programming. For example, if you use threading to save images, you will need find a way to name each image uniquely; a frame counter won't work because two different threads might read the counter at the same time, causing the image data of one thread to overwrite the other.

***

**This is the last document in the "Write Data" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [object_data_json.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/read_write/object_data_json.py) Write object positions and rotations to JSON files using a custom sub-class of `ObjectManager`.

Python API:

- [`OutputDataWriter`](../../python/add_ons/output_data_writer.md)
- [`ObjectManager`](../../python/add_ons/object_manager.md)
