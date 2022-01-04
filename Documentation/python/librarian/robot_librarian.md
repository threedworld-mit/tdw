# Robot Librarian

A **Robot Librarian** is a robot records database.

## Default Libraries

There is only one robot library: `robots.json`. You can define it explicitly, or not.

```python
from tdw.librarian import RobotLibrarian

# These constructors will load the same records database.
lib = RobotLibrarian()
lib = RobotLibrarian(library="robots.json")

# Get the names of all records in the library.
for record in lib.records:
    print(record.name)
```

## Command API

Send the `add_robot` command to add a robot to the scene or use the wrapper function `Controller.get_add_robot()`:

```python
from platform import system
from tdw.backend.platforms import SYSTEM_TO_S3
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

if __name__ == "__main__":
    c = Controller(launch_build=False)
    c.start()
    
    commands = [TDWUtils.create_empty_room(12, 12)]
    
    # Add a robot to the scene.
    commands.append({"$type": "add_robot",
                     "id": 0,
                     "position": {"x": 1, "y": 0, "z": 0},
                     "rotation": 0,
                     "name": "ur3",
                     "url": f"https://tdw-public.s3.amazonaws.com/robots/{SYSTEM_TO_S3[system()]}/2020.2/ur3"})
    # This is identical to the `add_robot` command, but uses a simpler wrapper function.
    commands.append(c.get_add_robot(name="ur3",
                                    robot_id=1,
                                    position={"x": -1, "y": 0, "z": 0},
                                    rotation=0))
    c.communicate(commands)
```

## RobotRecord API

A record of a robot asset bundle.

```python
from tdw.librarian import RobotRecord

record = RobotRecord() # Creates a record with blank or default values.
```

```python
from tdw.librarian import RobotRecord

record = RobotRecord(data=data) # Creates a record from JSON data.
```

### Fields

| Field       | Type           | Description                                                  |
| ----------- | -------------- | ------------------------------------------------------------ |
| `name`      | str            | The name of the robot.                                       |
| `urls`      | Dict[str, str] | A dictionary of URLs or local filepaths of asset bundles per platform. See: `RobotRecord.get_url()` |
| `source`    | str            | The source URL of the robot model or .urdf file.             |
| `immovable` | bool           | If true, the base of the robot is immovable and can't change position once added to the scene. |
| `targets`   | dict           | A dictionary of "canonical" joint targets to set a pose such that none of the joints are intersecting with the floor, assuming that the robot's starting position is (0, 0, 0). Key = The name of the joint. Value = A dictionary: `"type"` is the type of joint (`"revolute"`, `"prismatic"`, `"sphereical"`) and `"target"` is the target angle or position. |
| `ik`        | list           | A list of joint link chains that can be used for inverse kinematics (IK). |

### Functions

##### `def get_url(self) -> str:`

Returns the URL of the asset bundle for this platform. This is a wrapper for `record.urls`.

```python
lib = RobotLibrarian()
record = lib.records[0]

print(record.get_url())
```

***

## RobotLibrarian API

### Fields

| Field         | Type              | Description                                                  |
| ------------- | ----------------- | ------------------------------------------------------------ |
| `library`     | str               | The path to the records database file.                       |
| `data`        | dict              | The raw JSON dictionary loaded from the records database file. |
| `description` | str               | A brief description of the library.                          |
| `records`     | List[RobotRecord] | The list of robot records.                                   |

### Static Functions

##### `def create_library(description: str, path: str) -> None:`

Create a new library JSON file.

```python
RobotRecord.create_library("My library", path="path/to/new/library.json")
```

| Parameter     | Type | Description                                               |
| ------------- | ---- | --------------------------------------------------------- |
| `description` | str  | A description of the library.                             |
| `path`        | str  | The absolute filepath to the .json records database file. |

***

##### `def get_library_filenames() -> List[str]:`

Returns a list of the filenames of the libraries of this type in the `tdw` module.

```python
filenames = RobotLibrarian.get_library_filenames()

print(filenames) # ['robots.json']
```

***

##### `def get_default_library() -> List[str]:`

Returns the filename of the default library (which is always the first element in the list returned by `get_library_filenames()`.

```python
default_library = RobotLibrarian.get_default_library()

print(default_library) # robots.json
```

### Functions

##### `def get_record(self, name: str) -> Optional[RobotRecord]:`

Returns a record with the specified name. If that record can't be found, returns None.

```python
lib = RobotLibrarian()
record = lib.get_record("ur3")

print(record.name) # ur3
```

| Parameter | Type | Description             |
| --------- | ---- | ----------------------- |
| `name`    | str  | The name of the record. |

***

##### `def search_records(self, search: str) -> List[RobotRecord]:`

Returns a list of records whose names include the search keyword.

```python
lib = RobotLibrarian()
records = lib.search_records("ur3")

for record in records:
    print(record.name) # ur3
```

| Parameter | Type | Description                                 |
| --------- | ---- | ------------------------------------------- |
| `search`  | str  | The string to search for in the robot name. |

***

##### `def add_or_update_record(self, record: RobotRecord, overwrite: bool, write bool  = True, quiet: bool = True) -> bool:`

Add a new record or update an existing record.

```python
record = define_record() # Provide your own code here.
lib = RobotLibrarian()

lib.add_or_update_record(record, False, write=True, quiet=False)
```

| Parameter   | Type        | Description                                                  |
| ----------- | ----------- | ------------------------------------------------------------ |
| `record`    | RobotRecord | The new or modified record.                                  |
| `overwrite` | bool        | **If True:** If there is a record with the same name as this record, replace it with the new record and return True. Otherwise, return False.<br>**If False:** If there is a record with the same name as this record, don't add the robot, and suggest a new name. |
| `write`     | bool        | If true, write the library data to disk  (overwriting the existing file). |
| `quiet`     | bool        | If true, don't print out messages to the console.            |

***

##### `def remove_record(self, record: Union[str, RobotRecord], write: bool = True) -> bool:`

Remove a record. Returns true if the record was removed.

```python
record = define_record() # Provide your own code here.
lib = RobotLibrarian()

lib.remove_record(record) # Returns False.
```

```python
lib = RobotLibrarian()

lib.remove_record("ur3") # Returns True.
```

| Parameter | Type                 | Description                                                  |
| --------- | -------------------- | ------------------------------------------------------------ |
| `record`  | RobotRecord _or_ str | The record or the name of the record.                        |
| `write`   | bool                 | If true, write the library data to disk  (overwriting the existing file). |

***

##### `def write(self, pretty=True) -> None:`

Write the library data to disk (overwriting the existing file).

| Parameter | Type | Description                                                  |
| --------- | ---- | ------------------------------------------------------------ |
| `pretty`  | bool | "Pretty print" the JSON data with line breaks and indentations. |

***

##### `def get_valid_record_name(self, name: str, overwrite: bool) -> Tuple[bool, str, List[str]]:`

Generates a valid record name. Returns: true if the name is good as-is, the new name, and a list of problems with the old name.

```python
lib = RobotLibrarian()

ok, name, problems = lib.get_valid_record_name("ur3", True)

print(ok) # True
print(name) # ur3
```

```python
lib = RobotLibrarian()

ok, name, problems = lib.get_valid_record_name("ur3", False)

print(ok) # False
print(name) # ur3
print(problems) # ["A record named ur3 already exists, and we don't want to overwrite it."]
```

| Parameter   | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| `name`      | str  | The name of a record we'd like to add.                       |
| `overwrite` | str  | **If True:** raise an exception if a record named `name` doesn't already exist.<br>**If False:** If the record exists, suggest a new name. |

***