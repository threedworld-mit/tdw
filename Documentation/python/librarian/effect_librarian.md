# Effect ibrarian

An **Effect Librarian** is a non-physics effect objects records database. Use this metadata in conjunction with effects.

## Default Libraries

There is only one non-physics object library: `effects.json`. You can define it explicitly, or not.

```python
from tdw.librarian import EffectLibrarian

# These constructors will load the same records database.
lib = EffectLibrarian()
lib = EffectLibrarian(library="effects.json")
```

## Command API

Send the `add_effect` command to add a robot to the scene or use the wrapper function `Controller.get_add_effect(name, id, position, rotation, library)`.

## EffectRecord API

A record of a non-physics effect object asset bundle.

```python
from tdw.librarian import EffectRecord 

record = EffectRecord() # Creates a record with blank or default values.
```

```python
from tdw.librarian import EffectRecord 

record = EffectRecord(data=data) # Creates a record from JSON data.
```

### Fields

| Field         | Type           | Description                                                  |
| ------------- | -------------- | ------------------------------------------------------------ |
| `name`        | str            | The name of the record.                                      |
| `object_type` | str            | The object type. This tells TDW how to load the object and which API commands are valid for this object. |
| `urls`        | Dict[str, str] | A dictionary of URLs or local filepaths of asset bundles per platform. See: `EffectRecord.get_url()` |

### Functions

##### `def get_url(self) -> str:`

Returns the URL of the asset bundle for this platform. This is a wrapper for `record.urls`.

```python
lib = EffectLibrarian()
record = lib.records[0]

print(record.get_url())
```

***

## EffectLibrarian API

### Fields

| Field         | Type               | Description                                                  |
| ------------- | ------------------ | ------------------------------------------------------------ |
| `library`     | str                | The path to the records database file.                       |
| `data`        | dict               | The raw JSON dictionary loaded from the records database file. |
| `description` | str                | A brief description of the library.                          |
| `records`     | List[EffectRecord] | The list of non-physics object records.                      |

### Static Functions

##### `def create_library(description: str, path: str) -> None:`

Create a new library JSON file.

```python
EffectLibrarian.create_library("My library", path="path/to/new/library.json")
```

| Parameter     | Type | Description                                               |
| ------------- | ---- | --------------------------------------------------------- |
| `description` | str  | A description of the library.                             |
| `path`        | str  | The absolute filepath to the .json records database file. |

***

##### `def get_library_filenames() -> List[str]:`

Returns a list of the filenames of the libraries of this type in the `tdw` module.

```python
filenames = EffectLibrarian.get_library_filenames()

print(filenames) # ['effects.json']
```

***

##### `def get_default_library() -> List[str]:`

Returns the filename of the default library (which is always the first element in the list returned by `get_library_filenames()`.

```python
default_library = EffectLibrarian.get_default_library()

print(default_library) # effects.json
```

### Functions

##### `def get_record(self, name: str) -> Optional[EffectRecord]:`

Returns a record with the specified name. If that record can't be found, returns None.

```python
lib = EffectLibrarian()
record = lib.get_record("burned_wood+0")

print(record.name) # burned_wood_0
```

| Parameter | Type | Description             |
| --------- | ---- | ----------------------- |
| `name`    | str  | The name of the record. |

***

##### `def search_records(self, search: str) -> List[EffectRecord]:`

Returns a list of records whose names include the search keyword.

```python
lib = EffectLibrarian()
records = lib.search_records("wood")

for record in records:
    print(record.name) # burned_wood_0, etc.
```

| Parameter | Type | Description                                  |
| --------- | ---- | -------------------------------------------- |
| `search`  | str  | The string to search for in the record name. |

***

##### `def add_or_update_record(self, record: EffectRecord, overwrite: bool, write bool  = True, quiet: bool = True) -> bool:`

Add a new record or update an existing record.

```python
record = define_record() # Provide your own code here.
lib = EffectLibrarian()

lib.add_or_update_record(record, False, write=True, quiet=False)
```

| Parameter   | Type         | Description                                                  |
| ----------- | ------------ | ------------------------------------------------------------ |
| `record`    | EffectRecord | The new or modified record.                                  |
| `overwrite` | bool         | **If True:** If there is a record with the same name as this record, replace it with the new record and return True. Otherwise, return False.<br>**If False:** If there is a record with the same name as this record, don't add the record, and suggest a new name. |
| `write`     | bool         | If true, write the library data to disk  (overwriting the existing file). |
| `quiet`     | bool         | If true, don't print out messages to the console.            |

***

##### `def remove_record(self, record: Union[str, EffectRecord], write: bool = True) -> bool:`

Remove a record. Returns true if the record was removed.

```python
record = define_record() # Provide your own code here.
lib = EffectLibrarian()

lib.remove_record(record) # Returns False.
```

```python
lib = EffectLibrarian()

lib.remove_record("burned_wood_0") # Returns True.
```

| Parameter | Type                 | Description                                                  |
| --------- | -------------------- | ------------------------------------------------------------ |
| `record`  | EffectRecord_or_ str | The record or the name of the record.                        |
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
lib = EffectLibrarian()

ok, name, problems = lib.get_valid_record_name("burned_wood_0", False)

print(ok) # False
print(name) # burned_wood_0abcd
print(problems) # ["A record named burned_wood_0 already exists, and we don't want to overwrite it."]
```

| Parameter   | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| `name`      | str  | The name of a record we'd like to add.                       |
| `overwrite` | str  | **If True:** raise an exception if a record named `name` doesn't already exist.<br>**If False:** If the record exists, suggest a new name. |

***