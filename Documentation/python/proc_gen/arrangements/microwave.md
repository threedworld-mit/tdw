# Microwave

`from proc_gen.arrangements.microwave import Microwave`

A microwave can have objects on top of it and inside of it.

- The microwave model is chosen randomly; see `Microwave.MODEL_CATEGORIES["microwave"]`
- A microwave always has a rectangular arrangement of objects on top of it. The objects are chosen randomly; see `Microwave.ON_TOP_OF["microwave"]`.
- A microwave may have a [`Plate`](plate.md) inside it; see `plate_probability` in the constructor. The plate will always have food on it.
- All microwaves have a door that can be opened.
- The root object of the microwave is kinematic and the door sub-object is non-kinematic.

***

## Functions

#### \_\_init\_\_

**`Microwave(plate_probability, wall, position)`**

**`Microwave(plate_probability, wall, position, model=None, rng=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| plate_probability |  float |  | The probability of placing a plate with food inside the microwave. |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| model |  Union[str, ModelRecord] | None | Either the name of the model (in which case the model must be in `models_core.json`, or a `ModelRecord`, or None. If None, a random model in the category is selected. |
| rng |  np.random.RandomState  | None | The random number generator. If None, a new random number generator is created. |

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

#### get_length

**`self.get_length()`**

_Returns:_  The lateral extent of the object.



