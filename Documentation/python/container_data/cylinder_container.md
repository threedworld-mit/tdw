# CylinderContainer

`from tdw.container_data.cylinder_container import CylinderContainer`

A cylindrical container shape.

***

## Fields

- `radius` The radius of the cylinder.

- `height` The height of the cylinder.

- `rotation` The rotation of the cylinder relative to the parent object in Euler angles.

- `tag` The collider's semantic [`ContainerTag`](container_tag.md).

- `position` The position of the shape relative to the parent object.

***

## Functions

#### \_\_init\_\_

**`CylinderContainer(tag, position, radius, height, rotation)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tag |  ContainerTag |  | The cylinder's semantic [`ContainerTag`](container_tag.md). |
| position |  Dict[str, float] |  | The position of the cylinder relative to the parent object. |
| radius |  float |  | The radius of the cylinder. |
| height |  float |  | The height of the cylinder. |
| rotation |  Dict[str, float] |  | The rotation of the cylinder relative to the parent object in Euler angles. |