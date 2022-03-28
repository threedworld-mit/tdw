# EdgeEmitter

`from tdw.obi_data.fluids.edge_emitter import EdgeEmitter`

A linear-shaped Obi fluid emitter.

***

## Fields

- `length` The length of the edge.

- `radial_velocity` The velocity twisting along the length of the edge.

***

## Functions

#### \_\_init\_\_

**`EdgeEmitter()`**

**`EdgeEmitter(length=0.1, radial_velocity=1)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| length |  float  | 0.1 | The length of the edge. |
| radial_velocity |  float  | 1 | The velocity twisting along the length of the edge. |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.