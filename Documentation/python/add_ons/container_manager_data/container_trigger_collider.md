# ContainerTriggerCollider

`from tdw.add_ons.container_manager_data.container_trigger_collider import ContainerTriggerCollider`

Data for a container trigger collider.

***

## Fields

- `tag` The collider's semantic [`ContainerColliderTag`](container_collider_tag.md).

- `position` The collider's local position.

- `shape` The [`TriggerColliderShape`](../../collision_data/trigger_collider_shape.md).

***

## Functions

#### \_\_init\_\_

**`ContainerTriggerCollider(tag, position)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| tag |  ContainerColliderTag |  | The collider's semantic [`ContainerColliderTag`](container_collider_tag.md). |
| position |  Dict[str, float] |  | The local position of the collider. |

