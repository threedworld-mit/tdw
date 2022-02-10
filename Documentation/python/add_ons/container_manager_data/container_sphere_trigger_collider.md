# ContainerSphereTriggerCollider

`from tdw.add_ons.container_manager_data.container_sphere_trigger_collider import ContainerSphereTriggerCollider`

Data for a container trigger sphere collider.

***

## Fields

- `tag` The collider's semantic [`ContainerColliderTag`](container_collider_tag.md).

- `position` The collider's local position.

- `shape` The [`TriggerColliderShape`](../../collision_data/trigger_collider_shape.md).

- `diameter` The diameter of the collider.

***

## Functions

#### \_\_init\_\_

**`ContainerSphereTriggerCollider(tag, position, diameter)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tag |  ContainerColliderTag |  | The collider's semantic [`ContainerColliderTag`](container_collider_tag.md). |
| position |  Dict[str, float] |  | The local position of the collider. |
| diameter |  float |  | The diameter of the collider. |

