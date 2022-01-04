# Humanoid Animation Librarian

A **Humanoid Animation Librarian** is a humanoid animation records database. Use this metadata in conjunction with [humanoids](humanoid_librarian.md).

## Default Libraries

There is only one humanoid animation library: `humanoid_animations.json`. You can define it explicitly, or not.

```python
from tdw.librarian import HumanoidAnimationLibrarian

# These constructors will load the same records database.
lib = HumanoidAnimationLibrarian()
lib = HumanoidAnimationLibrarian(library="humanoid_animations.json")
```

## Command API

**TODO**

## HumanoidAnimationRecord API

A record of a humanoid animation asset bundle.

```python
from tdw.librarian import HumanoidAnimationRecord

record = HumanoidAnimationRecord() # Creates a record with blank or default values.
```

```python
from tdw.librarian import HumanoidAnimationRecord

record = HumanoidAnimationRecord(data=data) # Creates a record from JSON data.
```

### Fields

| Field       | Type           | Description                                                  |
| ----------- | -------------- | ------------------------------------------------------------ |
| `name`      | str            | The name of the animation.                                   |
| `urls`      | Dict[str, str] | A dictionary of URLs or local filepaths of asset bundles per platform. See: `HumanoidAnimationRecord.get_url()` |
| `duration`  | float          | The duration of the animation in seconds.                    |
| `framerate` | int            | Animation frames per second. This is _not_ the same thing as TDW framerate. |
| `loop`      | bool           | Whether this animation is a seamless loop.                   |

### Functions

##### `def get_url(self) -> str:`

Returns the URL of the asset bundle for this platform. This is a wrapper for `record.urls`.

```python
lib = HumanoidAnimationLibrarian()
record = lib.records[0]

print(record.get_url())
```

##### `def get_num_frames(self) -> str:`

Returns the number of frames, assuming a animation framerate of 120 FPS. (This is not the same as the TDW FPS!)


```python
lib = HumanoidLibrarian()
record = lib.records[0]

print(record.get_num_frames()) # 741
```

***

## HumanoidAnimationLibrarian API

### Fields

| Field         | Type                          | Description                                                  |
| ------------- | ----------------------------- | ------------------------------------------------------------ |
| `library`     | str                           | The path to the records database file.                       |
| `data`        | dict                          | The raw JSON dictionary loaded from the records database file. |
| `description` | str                           | A brief description of the library.                          |
| `records`     | List[HumanoidAnimationRecord] | The list of animation records.                               |

### Static Functions

##### `def create_library(description: str, path: str) -> None:`

Create a new library JSON file.

```python
HumanoidAnimationRecord.create_library("My library", path="path/to/new/library.json")
```

| Parameter     | Type | Description                                               |
| ------------- | ---- | --------------------------------------------------------- |
| `description` | str  | A description of the library.                             |
| `path`        | str  | The absolute filepath to the .json records database file. |

***

##### `def get_library_filenames() -> List[str]:`

Returns a list of the filenames of the libraries of this type in the `tdw` module.

```python
filenames = HumanoidAnimationLibrarian.get_library_filenames()

print(filenames) # ['humanoid_animations.json']
```

***

##### `def get_default_library() -> List[str]:`

Returns the filename of the default library (which is always the first element in the list returned by `get_library_filenames()`.

```python
default_library = HumanoidAnimationLibrarian.get_default_library()

print(default_library) # hunanoid_animations.json
```

### Functions

##### `def get_record(self, name: str) -> Optional[HumanoidAnimationRecord]:`

Returns a record with the specified name. If that record can't be found, returns None.

```python
lib = HumanoidAnimationLibrarian()
record = lib.get_record("archery")

print(record.name) # archery
```

| Parameter | Type | Description             |
| --------- | ---- | ----------------------- |
| `name`    | str  | The name of the record. |

***

##### `def search_records(self, search: str) -> List[HumanoidAnimationRecord]:`

Returns a list of records whose names include the search keyword.

```python
lib = HumanoidAnimationLibrarian()
records = lib.search_records("walk")

for record in records:
    print(record.name) # walking_1, walking_2, etc.
```

| Parameter | Type | Description                                     |
| --------- | ---- | ----------------------------------------------- |
| `search`  | str  | The string to search for in the animation name. |

***

##### `def add_or_update_record(self, record: HumanoidAnimationRecord, overwrite: bool, write bool  = True, quiet: bool = True) -> bool:`

Add a new record or update an existing record.

```python
record = define_record() # Provide your own code here.
lib = HumanoidAnimationLibrarian()

lib.add_or_update_record(record, False, write=True, quiet=False)
```

| Parameter   | Type                    | Description                                                  |
| ----------- | ----------------------- | ------------------------------------------------------------ |
| `record`    | HumanoidAnimationRecord | The new or modified record.                                  |
| `overwrite` | bool                    | **If True:** If there is a record with the same name as this record, replace it with the new record and return True. Otherwise, return False.<br>**If False:** If there is a record with the same name as this record, don't add the animation, and suggest a new name. |
| `write`     | bool                    | If true, write the library data to disk  (overwriting the existing file). |
| `quiet`     | bool                    | If true, don't print out messages to the console.            |

***

##### `def remove_record(self, record: Union[str, HumanoidAnimationRecord], write: bool = True) -> bool:`

Remove a record. Returns true if the record was removed.

```python
record = define_record() # Provide your own code here.
lib = HumanoidAnimationLibrarian()

lib.remove_record(record) # Returns False.
```

```python
lib = HumanoidAnimationLibrarian()

lib.remove_record("archery") # Returns True.
```

| Parameter | Type                             | Description                                                  |
| --------- | -------------------------------- | ------------------------------------------------------------ |
| `record`  | HumanoidAnimationRecord _or_ str | The record or the name of the record.                        |
| `write`   | bool                             | If true, write the library data to disk  (overwriting the existing file). |

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
lib = HumanoidAnimationLibrarian()

ok, name, problems = lib.get_valid_record_name("archery", False)

print(ok) # False
print(name) # archerabcd
print(problems) # ["A record named archery already exists, and we don't want to overwrite it."]
```

| Parameter   | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| `name`      | str  | The name of a record we'd like to add.                       |
| `overwrite` | str  | **If True:** raise an exception if a record named `name` doesn't already exist.<br>**If False:** If the record exists, suggest a new name. |

***