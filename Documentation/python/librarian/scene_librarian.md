# Scene Librarian

A **Scene Librarian** is a scene records database. 

A **scene** is the background environment in TDW. You must load a scene before anything else.

You can alternatively load the "Proc Gen Room" via `create_exterior_walls`, which is _not_ an asset bundle (and therefore doesn't have a record).

```python
from tdw.librarian import SceneLibrarian

lib = SceneLibrarian()
```

```python
from tdw.librarian import SceneLibrarian

lib = SceneLibrarian(library="path/to/your/database/file.json")
```

A Scene Librarian contains `SceneRecord` objects.

```python
record = lib.records[0]
print(record.name) # abandoned_factory
```

## Default Libraries

There is only one scene library: `scenes.json`. You can define it explicitly, or not.

```python
from tdw.librarian import SceneLibrarian

# These constructors will load the same records database.
lib = SceneLibrarian()
lib = SceneLibrarian(library="scenes.json")
```

## Command API

Send the `add_scene` command to load a scene from a remote or local asset bundle.

```python
from tdw.controller import Controller

c = Controller()

init(c) # Initialize the scene. Your code here.
record = get_record() # Get a scene record. Your code here.

c.communicate({"$type": "add_scene",
                "name": record.name,
                "url": record.get_url()})
```

The `Controller` class includes a few helper functions for loading scenes. See the [Controller documentation](../controller.md).

## SceneRecord API

A record of a scene asset bundle.

```python
from tdw.librarian import SceneRecord

record = SceneRecord() # Creates a record with blank or default values.
```

```python
from tdw.librarian import SceneRecord

record = SceneRecord(data=data) # Creates a record from JSON data.
```

### Fields

| Field         | Type           | Description                                                  |
| ------------- | -------------- | ------------------------------------------------------------ |
| `name`        | str            | The name of the scene.                                       |
| `urls`        | Dict[str, str] | A dictionary of URLs or local filepaths of asset bundles per platform. See: `SceneRecord.get_url()` |
| `description` | str            | A brief description of the scene.                            |
| `location`    | str            | Whether the scene is indoor or outdoor.                      |
| `hdri`        | bool           | If true, HDRI skyboxes can be used with this scene.          |

### Functions

##### `def get_url(self) -> str:`

Returns the URL of the asset bundle for this platform. This is a wrapper for `record.urls`.

```python
lib = SceneLibrarian()
record = lib.records[0]

print(record.get_url())
```

***

## SceneLibrarian API

### Fields

| Field         | Type              | Description                                                  |
| ------------- | ----------------- | ------------------------------------------------------------ |
| `library`     | str               | The path to the records database file.                       |
| `data`        | dict              | The raw JSON dictionary loaded from the records database file. |
| `description` | str               | A brief description of the library.                          |
| `records`     | List[SceneRecord] | The list of scene records.                                   |

### Static Functions

##### `def create_library(description: str, path: str) -> None:`

Create a new library JSON file.

```python
SceneLibrarian.create_library("My library", path="path/to/new/library.json")
```

| Parameter     | Type | Description                                               |
| ------------- | ---- | --------------------------------------------------------- |
| `description` | str  | A description of the library.                             |
| `path`        | str  | The absolute filepath to the .json records database file. |

***

##### `def get_library_filenames() -> List[str]:`

Returns a list of the filenames of the libraries of this type in the `tdw` module.

```python
filenames = SceneLibrarian.get_library_filenames()

print(filenames) # ['scenes.json']
```

***

##### `def get_default_library() -> List[str]:`

Returns the filename of the default library (which is always the first element in the list returned by `get_library_filenames()`.

```python
default_library = SceneLibrarian.get_default_library()

print(default_library) # scenes.json
```

### Functions

##### `def get_record(self, name: str) -> Optional[SceneRecord]:`

Returns a record with the specified name. If that record can't be found, returns None.

```python
lib = SceneLibrarian()
record = lib.get_record("tdw_room")

print(record.name) # tdw_room
```

| Parameter | Type | Description             |
| --------- | ---- | ----------------------- |
| `name`    | str  | The name of the record. |

***

##### `def search_records(self, search: str) -> List[SceneRecord]:`

Returns a list of records whose names include the search keyword.

```python
lib = SceneLibrarian()
records = lib.search_records("room")

for record in records:
    print(record.name) # box_room_2018, monkey_physics_room, etc.
```

| Parameter | Type | Description                                 |
| --------- | ---- | ------------------------------------------- |
| `search`  | str  | The string to search for in the scene name. |

***

##### `def add_or_update_record(self, record: SceneRecord, overwrite: bool, write bool  = True, quiet: bool = True) -> bool:`

Add a new record or update an existing record.

```python
record = define_record() # Provide your own code here.
lib = SceneLibrarian()

lib.add_or_update_record(record, False, write=True, quiet=False)
```

| Parameter   | Type        | Description                                                  |
| ----------- | ----------- | ------------------------------------------------------------ |
| `record`    | SceneRecord | The new or modified record.                                  |
| `overwrite` | bool        | **If True:** If there is a record with the same name as this record, replace it with the new record and return True. Otherwise, return False.<br>**If False:** If there is a record with the same name as this record, don't add the scene, and suggest a new name. |
| `write`     | bool        | If true, write the library data to disk  (overwriting the existing file). |
| `quiet`     | bool        | If true, don't print out messages to the console.            |

***

##### `def remove_record(self, record: Union[str, SceneRecord], write: bool = True) -> bool:`

Remove a record. Returns true if the record was removed.

```python
record = define_record() # Provide your own code here.
lib = SceneLibrarian()

lib.remove_record(record) # Returns False.
```

```python
lib = SceneLibrarian()

lib.remove_record("tdw_room") # Returns True.
```

| Parameter | Type                 | Description                                                  |
| --------- | -------------------- | ------------------------------------------------------------ |
| `record`  | SceneRecord _or_ str | The record or the name of the record.                        |
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
lib = SceneLibrarian()

ok, name, problems = lib.get_valid_record_name("tdw_room", True)

print(ok) # True
print(name) # tdw_room
```

```python
lib = SceneLibrarian()

ok, name, problems = lib.get_valid_record_name("tdw_room", False)

print(ok) # False
print(name) # tdw_roomabcd
print(problems) # ["A record named tdw_room already exists, and we don't want to overwrite it."]
```

| Parameter   | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| `name`      | str  | The name of a record we'd like to add.                       |
| `overwrite` | str  | **If True:** raise an exception if a record named `name` doesn't already exist.<br>**If False:** If the record exists, suggest a new name. |

***