# `flex/fluid_types.py`

## `FluidType`

`from tdw.flex.fluid_types import FluidType`

Metadata for a single fluid type. Specifies values for Flex fluid containers.

***

#### `__init__(self, fluid_type: str, viscosity: float, adhesion: float, cohesion: float)`


| Parameter | Description |
| --- | --- |
| fluid_type | Name of the fluid type. |
| viscosity | The viscosity value of the fluid. |
| adhesion | The adhesion value of the fluid. |
| cohesion | The cohesion value of the fluid. |

***

## `FluidTypes`

`from tdw.flex.fluid_types import FluidTypes`

Manage data for available fluid types, as defined in JSON data file.

Usage:

```python
from tdw.flex.fluid_types import FluidTypes

ft = FluidTypes()

print(ft.fluid_type_names) # ["water", "ink", ... ]

water = ft.fluid_types["water"]
print(water.fluid_type) # "water"
```

***

#### `__init__(self)`

***

