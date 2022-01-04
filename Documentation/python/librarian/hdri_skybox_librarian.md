# HDRI Skybox Librarian

An  **HDRI Skybox Librarian** is an HDRI skybox records database. 

An **HDRI skybox** is a background image with real-world lighting data. See the `hdri.py` example controller.

```python
from tdw.librarian import HDRISkyboxLibrarian

lib = HDRISkyboxLibrarian()
```

```python
from tdw.librarian import HDRISkyboxLibrarian

lib = HDRISkyboxLibrarian(library="path/to/your/database/file.json")
```

An HDRI Skybox Librarian contains `HDRISkyboxRecord` objects.

```python
record = lib.records[0]
print(record.name) # aft_lounge_4k
```

## Default Libraries

There is only one HDRI skybox library: `hdri_skyboxes.json`. You can define it explicitly, or not.

```python
from tdw.librarian import HDRISkyboxLibrarian

# These constructors will load the same records database.
lib = HDRISkyboxLibrarian()
lib = HDRISkyboxLibrarian(library="hdri_skyboxes.json")
```

## Command API

Send the `add_hdri_skybox` command to add an HDRI skybox from a remote or local asset bundle.

```python
from tdw.controller import Controller

c = Controller()

init(c) # Initialize the scene. Your code here.
record = get_record() # Get an HDRI skybox record. Your code here.

c.communicate({"$type": "add_hdri_skybox",
                "name": record.name,
                "url": record.get_url(),
                "exposure": record.exposure,
                "initial_skybox_rotation": record.initial_skybox_rotation,
                "sun_elevation": record.sun_elevation,
                "sun_initial_angle": record.sun_initial_angle,
                "sun_intensity": record.sun_intensity})
```

The `Controller` class includes a few helper functions for adding HDRI skyboxes. See the [Controller documentation](../controller.md).

## HDRISkyboxRecord API

A record of an HDRI Skybox asset bundle.

```python
from tdw.librarian import HDRISkyboxRecord 

record = HDRISkyboxRecord () # Creates a record with blank or default values.
```

```python
from tdw.librarian import HDRISkyboxRecord 

record = HDRISkyboxRecord(data=data) # Creates a record from JSON data.
```

### Fields

| Field                    | Type           | Description                                                  |
| ------------------------ | -------------- | ------------------------------------------------------------ |
| `name`                   | str            | The name of the skybox.                                      |
| `urls`                   | Dict[str, str] | A dictionary of URLs or local filepaths of asset bundles per platform. See: `HDRISkyboxRecord.get_url()` |
| `color_temperature`      | float          |                                                              |
| `sun_elevation`          | float          |                                                              |
| `sun_initial_angle`      | float          |                                                              |
| `sun_intensity`          | float          |                                                              |
| `intial_skybox_rotation` | float          |                                                              |
| `exposure`               | float          |                                                              |
| `location`               | str            | Interior or exterior. Useful for deciding what skybox to load. |

### Functions

##### `def get_url(self) -> str:`

Returns the URL of the asset bundle for this platform. This is a wrapper for `record.urls`.

```python
lib = HDRISkyboxLibrarian()
record = lib.records[0]

print(record.get_url())
```

***

## HDRISkyboxLibrarian API

### Fields

| Field         | Type                   | Description                                                  |
| ------------- | ---------------------- | ------------------------------------------------------------ |
| `library`     | str                    | The path to the records database file.                       |
| `data`        | dict                   | The raw JSON dictionary loaded from the records database file. |
| `description` | str                    | A brief description of the library.                          |
| `records`     | List[HDRISkyboxRecord] | The list of HDRI skybox records.                             |

### Static Functions

##### `def create_library(description: str, path: str) -> None:`

Create a new library JSON file.

```python
HDRISkyboxLibrarian.create_library("My library", path="path/to/new/library.json")
```

| Parameter     | Type | Description                                               |
| ------------- | ---- | --------------------------------------------------------- |
| `description` | str  | A description of the library.                             |
| `path`        | str  | The absolute filepath to the .json records database file. |

***

##### `def get_library_filenames() -> List[str]:`

Returns a list of the filenames of the libraries of this type in the `tdw` module.

```python
filenames = HDRISkyboxLibrarian.get_library_filenames()

print(filenames) # ['hdri_skyboxes.json']
```

***

##### `def get_default_library() -> List[str]:`

Returns the filename of the default library (which is always the first element in the list returned by `get_library_filenames()`.

```python
default_library = HDRISkyboxLibrarian.get_default_library()

print(default_library) # hdri_skyboxes.json
```

### Functions

##### `def get_record(self, name: str) -> Optional[HDRISkyboxRecord]:`

Returns a record with the specified name. If that record can't be found, returns None.

```python
lib = HDRISkyboxLibrarian()
record = lib.get_record("aft_lounge_4k")

print(record.name) # aft_lounge_4k
```

| Parameter | Type | Description             |
| --------- | ---- | ----------------------- |
| `name`    | str  | The name of the record. |

***

##### `def search_records(self, search: str) -> List[HDRISkyboxRecord]:`

Returns a list of records whose names include the search keyword.

```python
lib = HDRISkyboxLibrarian()
records = lib.search_records("lounge")

for record in records:
    print(record.name) # aft_lounge_4k
```

| Parameter | Type | Description                                  |
| --------- | ---- | -------------------------------------------- |
| `search`  | str  | The string to search for in the skybox name. |

***

##### `def add_or_update_record(self, record: HDRISkyboxRecord, overwrite: bool, write: bool = True, quiet: bool = True) -> bool:`

Add a new record or update an existing record.

```python
record = define_record() # Provide your own code here.
lib = HDRISkyboxLibrarian()

lib.add_or_update_record(record, False, write=True, quiet=False)
```

| Parameter   | Type             | Description                                                  |
| ----------- | ---------------- | ------------------------------------------------------------ |
| `record`    | HDRISkyboxRecord | The new or modified record.                                  |
| `overwrite` | bool             | **If True:** If there is a record with the same name as this record, replace it with the new record and return True. Otherwise, return False.<br>**If False:** If there is a record with the same name as this record, don't add the skybox, and suggest a new name. |
| `write`     | bool             | If true, write the library data to disk  (overwriting the existing file). |
| `quiet`     | bool             | If true, don't print out messages to the console.            |

***

##### `def remove_record(self, record: Union[str, HDRISkyboxRecord], write: bool = True) -> bool:`

Remove a record. Returns true if the record was removed.

```python
record = define_record() # Provide your own code here.
lib = HDRISkyboxLibrarian()

lib.remove_record(record) # Returns False.
```

```python
lib = HDRISkyboxLibrarian()

lib.remove_record("aft_lounge_4k") # Returns True.
```

| Parameter | Type                      | Description                                                  |
| --------- | ------------------------- | ------------------------------------------------------------ |
| `record`  | HDRISkyboxRecord _or_ str | The record or the name of the record.                        |
| `write`   | bool                      | If true, write the library data to disk  (overwriting the existing file). |

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
lib = HDRISkyboxLibrarian()

ok, name, problems = lib.get_valid_record_name("aft_lounge_4k", True)

print(ok) # True
print(name) # aft_lounge_4k
```

```python
lib = HDRISkyboxLibrarian()

ok, name, problems = lib.get_valid_record_name("aft_lounge_4k", False)

print(ok) # False
print(name) # aft_lounge_4kabcd
print(problems) # ["A record named aft_lounge_4k already exists, and we don't want to overwrite it."]
```

| Parameter   | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| `name`      | str  | The name of a record we'd like to add.                       |
| `overwrite` | str  | **If True:** raise an exception if a record named `name` doesn't already exist.<br>**If False:** If the record exists, suggest a new name. |

***