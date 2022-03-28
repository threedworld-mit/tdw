# DiskEmitter

`from tdw.obi_data.fluids.disk_emitter import DiskEmitter`

A disk-shaped Obi fluid emitter.

***

## Fields

- `radius` The radius of the circle.

- `edge_emission` If enabled, particles will be emitted from the circle's edges, instead of its interior.

***

## Functions

#### \_\_init\_\_

**`DiskEmitter()`**

**`DiskEmitter(radius=0.1, edge_emission=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| radius |  float  | 0.1 | The radius of the circle. |
| edge_emission |  bool  | False | If enabled, particles will be emitted from the circle's edges, instead of its interior. |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.