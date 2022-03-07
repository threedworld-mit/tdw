# KitchenCounterTopBase

`from proc_gen.arrangements.kitchen_counter_top_base import KitchenCounterTopBase`

Abstract base class for arrangments that including a floating kitchen counter top.

***

## Functions

#### \_\_init\_\_

**`KitchenCounterTopBase(cabinetry, wall, corner, distance, region)`**

**`KitchenCounterTopBase(cabinetry, wall, corner, distance, region, model=None, wall_length=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| cabinetry |  KitchenCabinetSet |  | The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md). |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| corner |  OrdinalDirection |  | The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction. |
| distance |  float |  | The distance in meters from the corner along the derived direction. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. If no model fits, the arrangement will not be added to the scene. |
| wall_length |  float  | None | The total length of the lateral arrangement. If None, defaults to the length of the wall. |
| rng |  np.random.RandomState  | None | The random number generator. If None, a new random number generator is created. |

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

#### get_length

**`self.get_length()`**

_Returns:_  The lateral extent of the object.



