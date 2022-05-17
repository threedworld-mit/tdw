# BoxContainer

`from tdw.container_data.box_container import BoxContainer`

A box-shaped container shape.

***

## Fields

- `half_extents` The half extents of the box.

- `rotation` The rotation of the box relative to the parent object in Euler angles.

- `tag` The collider's semantic [`ContainerTag`](container_tag.md).

- `position` The position of the shape relative to the parent object.

***

## Functions

#### \_\_init\_\_

**`BoxContainer(tag, position, half_extents, rotation)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tag |  ContainerTag |  | The box's semantic [`ContainerTag`](container_tag.md). |
| position |  Dict[str, float] |  | The position of the box relative to the parent object. |
| half_extents |  Dict[str, float] |  | The half extents of the box. |
| rotation |  Dict[str, float] |  | The rotation of the box relative to the parent object in Euler angles. |