# Material Librarian

A **Material Librarian** is a [material](../../lessons/scene_setup_low_level/materials_textures_colors.md) records database. 

```python
from tdw.librarian import MaterialLibrarian

lib = MaterialLibrarian()
```

```python
from tdw.librarian import MaterialLibrarian

lib = MaterialLibrarian(library="path/to/your/database/file.json")
```

A Material Librarian contains `MaterialRecord` objects.

```python
record = lib.records[0]
print(record.name, record.type) # 3d_mesh_technical_fabric Metal
```

## Default Libraries

TDW has three database files for three remote material libraries. Each material library has the exact same records, except that the URLs point to different _texture resolutions._ To access these files, just provide the filename in the constructor without a path, e.g.:

```python
from tdw.librarian import MaterialLibrarian

lib = MaterialLibrarian(library="materials_high.json")
```

If you don't provided a value for `library`, the default is `materials_med.json`.

| Library               | Texture Resolution |
| --------------------- | ------------------ |
| `materials_high.json` | 2048x2048          |
| `materials_med.json`  | 1024x1024          |
| `materials_low.json`  | 512x512            |

## Command API

Send the `add_material` command to add a material to the scene from a remote or local asset bundle. You must send this command before any other material commands (e.g. `set_visual_material`).

```python
from tdw.controller import Controller

c = Controller()

init(c) # Initialize the scene. Your code here.
record = get_record() # Get a material record. Your code here.

c.communicate({"$type": "add_material",
                "name": record.name,
                "url": record.get_url()})
```

The `Controller` class includes a few helper functions for using records to add materials to the scene. See the [Controller documentation](../controller.md).

## MaterialRecord API

A record of a material asset bundle. Each material has a "Semantic Material Type" such as "Wood" or "Metal" that can be used in the Command API as well as basic visual classification.

```python
from tdw.librarian import MaterialRecord 

record = MaterialRecord() # Creates a record with blank or default values.
```

```python
from tdw.librarian import MaterialRecord 

record = MaterialRecord(data=data) # Creates a record from JSON data.
```

### Fields

| Field  | Type           | Description                                                  |
| ------ | -------------- | ------------------------------------------------------------ |
| `name` | str            | The name of the model.                                       |
| `urls` | Dict[str, str] | A dictionary of URLs or local filepaths of asset bundles per platform. See: `ModelRecord.get_url()` |
| `type` | str            | The semantic material type of the material.                  |

### Functions

##### `def get_url(self) -> str:`

Returns the URL of the asset bundle for this platform. This is a wrapper for `record.urls`.

```python
lib = MaterialLibrarian()
record = lib.records[0]

print(record.get_url())
```

***

## MaterialLibrarian API

### Fields

| Field         | Type                 | Description                                                  |
| ------------- | -------------------- | ------------------------------------------------------------ |
| `library`     | str                  | The path to the records database file.                       |
| `data`        | dict                 | The raw JSON dictionary loaded from the records database file. |
| `description` | str                  | A brief description of the library.                          |
| `records`     | List[MaterialRecord] | The list of material records.                                |

### Static Functions

##### `def create_library(description: str, path: str) -> None:`

Create a new library JSON file.

```python
MaterialLibrarian.create_library("My library", path="path/to/new/library.json")
```

| Parameter     | Type | Description                                               |
| ------------- | ---- | --------------------------------------------------------- |
| `description` | str  | A description of the library.                             |
| `path`        | str  | The absolute filepath to the .json records database file. |

***

##### `def get_library_filenames() -> List[str]:`

Returns a list of the filenames of the libraries of this type in the `tdw` module.

```python
filenames = MaterialLibrarian.get_library_filenames()

print(filenames) # ['materials_med.json', 'materials_low.json', 'materials_high.json']
```

***

##### `def get_default_library() -> List[str]:`

Returns the filename of the default library (which is always the first element in the list returned by `get_library_filenames()`.

```python
default_library = MaterialLibrarian.get_default_library()

print(default_library) # materials_med.json
```

### Functions

##### `def get_record(self, name: str) -> Optional[ModelRecord]:`

Returns a record with the specified name. If that record can't be found, returns None.

```python
lib = MaterialLibrarian()
record = lib.get_record("3d_mesh_technical_fabric")

print(record.name) # 3d_mesh_technical_fabric
```

| Parameter | Type | Description             |
| --------- | ---- | ----------------------- |
| `name`    | str  | The name of the record. |

***

##### `def search_records(self, search: str) -> List[ModelRecord]:`

Returns a list of records whose names include the search keyword.

```python
lib = MaterialLibrarian()
records = lib.search_records("concrete")

for record in records:
    print(record.name) # concrete, concrete_01, etc.
```

| Parameter | Type | Description                                    |
| --------- | ---- | ---------------------------------------------- |
| `search`  | str  | The string to search for in the material name. |

***

##### `def add_or_update_record(self, record: MaterialRecord, overwrite: bool, write: bool = True, quiet: bool = True) -> bool:`

Add a new record or update an existing record.

```python
record = define_record() # Provide your own code here.
lib = MaterialLibrarian()

lib.add_or_update_record(record, False, write=True, quiet=False)
```

| Parameter   | Type           | Description                                                  |
| ----------- | -------------- | ------------------------------------------------------------ |
| `record`    | MaterialRecord | The new or modified record.                                  |
| `overwrite` | bool           | **If True:** If there is a record with the same name as this record, replace it with the new record and return True. Otherwise, return False.<br>**If False:** If there is a record with the same name as this record, don't add the model, and suggest a new name. |
| `write`     | bool           | If true, write the library data to disk  (overwriting the existing file). |
| `quiet`     | bool           | If true, don't print out messages to the console.            |

***

##### `def remove_record(self, record: Union[str, MaterialRecord], write: bool = True) -> bool:`

Remove a record. Returns true if the record was removed.

```python
record = define_record() # Provide your own code here.
lib = MaterialLibrarian()

lib.remove_record(record) # Returns False.
```

```python
lib = MaterialLibrarian()

lib.remove_record("concrete") # Returns True.
```

| Parameter | Type                    | Description                                                  |
| --------- | ----------------------- | ------------------------------------------------------------ |
| `record`  | MaterialRecord _or_ str | The record or the name of the record.                        |
| `write`   | bool                    | If true, write the library data to disk  (overwriting the existing file). |

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
lib = MaterialLibrarian()

ok, name, problems = lib.get_valid_record_name("concrete", True)

print(ok) # True
print(name) # concrete
```

```python
lib = MaterialLibrarian()

ok, name, problems = lib.get_valid_record_name("concrete", False)

print(ok) # False
print(name) # concreteabcd
print(problems) # ["A record named concrete already exists, and we don't want to overwrite it."]
```

| Parameter   | Type | Description                                                  |
| ----------- | ---- | ------------------------------------------------------------ |
| `name`      | str  | The name of a record we'd like to add.                       |
| `overwrite` | str  | **If True:** raise an exception if a record named `name` doesn't already exist.<br>**If False:** If the record exists, suggest a new name. |

***

##### `def get_all_materials_of_type(self, material_type: str) -> List[MaterialRecord]:`

Returns a list of all of the materials with the semantic material type.

```python
lib = MaterialLibrarian()
records = lib.get_all_materials_of_type("Ceramic")

print(records[0].name) # arabesque_tile_wall
```

| Parameter       | Type | Description                 |
| --------------- | ---- | --------------------------- |
| `material_type` | str  | The semantic material type. |

***

##### `def get_material_types(self) -> List[str]:`

Returns a list of all types of materials, sorted alphabetically.

```python
lib = MaterialLibrarian()
material_types = lib.get_material_types()

print(material_types[0]) # Ceramic
```