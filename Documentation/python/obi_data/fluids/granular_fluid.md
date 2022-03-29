# GranularFluid

`from tdw.obi_data.fluids.granular_fluid import GranularFluid`

Data for an Obi granular fluid. For more information, [read this](http://obi.virtualmethodstudio.com/tutorials/emittermaterials.html).

***

## Fields

- `randomness` The variation in particle size.

- `capacity` The maximum amount of emitted particles.

- `resolution` The size and amount of particles in 1 cubic meter.

- `color` The visual color of the fluid.

- `rest_density` The fluid density in kg/m3.

- `radius_scale` This scales the size at which particles are drawn.

- `random_velocity` Random velocity of emitted particles.

***

## Functions

#### \_\_init\_\_

**`GranularFluid(randomness, capacity, resolution, color, rest_density)`**

**`GranularFluid(randomness, capacity, resolution, color, rest_density, radius_scale=1.7, random_velocity=0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| randomness |  float |  | The variation in particle size. |
| capacity |  int |  | The maximum amount of emitted particles. |
| resolution |  float |  | The size and amount of particles in 1 cubic meter. |
| color |  Dict[str, float] |  | The visual color of the fluid. |
| rest_density |  float |  | The fluid density in kg/m3. |
| radius_scale |  float  | 1.7 | This scales the size at which particles are drawn. |
| random_velocity |  float  | 0 | Random velocity of emitted particles. |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.