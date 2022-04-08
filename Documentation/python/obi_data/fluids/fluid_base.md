# FluidBase

`from tdw.obi_data.fluids.fluid_base import FluidBase`

Abstract base class for Obi fluids.

***

## Fields

- `capacity` The maximum amount of emitted particles.

- `resolution` The size and amount of particles in 1 cubic meter.

- `color` The visual color of the fluid.

- `rest_density` The fluid density in kg/m3.

- `radius_scale` This scales the size at which particles are drawn.

- `random_velocity` Random velocity of emitted particles.

***

## Functions

#### \_\_init\_\_

**`FluidBase(capacity, resolution, color, rest_density)`**

**`FluidBase(capacity, resolution, color, rest_density, radius_scale=1.7, random_velocity=0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| capacity |  int |  | The maximum amount of emitted particles. |
| resolution |  float |  | The size and amount of particles in 1 cubic meter. |
| color |  Dict[str, float] |  | The visual color of the fluid. |
| rest_density |  float |  | The fluid density in kg/m3. |
| radius_scale |  float  | 1.7 | This scales the size at which particles are drawn. |
| random_velocity |  float  | 0 | Random velocity of emitted particles. |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.