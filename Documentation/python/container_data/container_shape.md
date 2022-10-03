# ContainerShape

`from tdw.container_data.container_shape import ContainerShape`

Abstract base class for container shapes, which are used to detect containment events.

***

## Fields

- `tag` The collider's semantic [`ContainerTag`](container_tag.md).

- `position` The position of the shape relative to the parent object.

***

## Functions

#### \_\_init\_\_

**`ContainerShape(tag, position)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tag |  ContainerTag |  | The shapes's semantic [`ContainerTag`](container_tag.md). |
| position |  Dict[str, float] |  | The position of the shape relative to the parent object. |