# SphereContainer

`from tdw.container_data.sphere_container import SphereContainer`

A spherical container shape.

***

## Fields

- `radius` The radius of the sphere.

- `tag` The collider's semantic [`ContainerTag`](container_tag.md).

- `position` The position of the shape relative to the parent object.

***

## Functions

#### \_\_init\_\_

**`SphereContainer(tag, position, radius)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tag |  ContainerTag |  | The sphere's semantic [`ContainerTag`](container_tag.md). |
| position |  Dict[str, float] |  | The position of the sphere relative to the parent object. |
| radius |  float |  | The radius of the sphere. |