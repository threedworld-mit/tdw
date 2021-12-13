##### 3D Model Libraries

# Overview

In most of the tutorials and documentation for TDW, as well as most example controllers and high-level APIs, the controller only uses the *default* [models](../core_concepts/objects.md) from the "core" [model library](../../python/librarian/model_librarian.md). These are free models that anyone can use in TDW.

This:

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian()
for record in librarian.records:
    print(record.name)
```

...is the same as this:

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian("models_core.json")
for record in librarian.records:
    print(record.name)
```

However, there are other model libraries in TDW. Some have free models and others have non-free models that require an access key.

| Model library         | Description                                       | Free |
| --------------------- | ------------------------------------------------- | ---- |
| `models_core.json`    | Approximately 400 models.                         | Yes  |
| `models_full.json`    | Approximately 2400 models.                        | No   |
| `models_special.json` | Primitives and special-purpose models.            | Yes  |
| `models_flex.json`    | Primitives optimized for NVIDIA Flex simulations. | Yes  |

You can also import models into TDW and define custom model libraries.

This tutorial will cover the other model libraries in TDW and how to add your own models to TDW.

## How to add objects from non-default model libraries into a scene

Set the `library` parameter of `c.get_add_object()`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="cube",
                                library="models_flex.json",
                                position={"x": 0, "y": 0, "z": 0,},
                                object_id=c.get_unique_id())])
```

***

**Next: [Free models](free_models.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`ModelLibrarian`](../../python/librarian/model_librarian.md)