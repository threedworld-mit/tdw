# ContainmentEvent

`from tdw.add_ons.container_manager_data.containment_event import ContainmentEvent`

Data describing a containment event i.e. when a container's trigger colliders enter or stay with another object.

***

## Fields

- `container_id` The ID of the container.

- `object_id` The ID of the contained object.

- `tag` A [`ContainerColliderTag`](container_collider_tag.md) describing the semantic nature of the event.

***

## Functions

#### \_\_init\_\_

**`ContainmentEvent(container_id, object_id, tag)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| container_id |  int |  | The ID of the container. |
| object_id |  int |  | The ID of the contained object. |
| tag |  ContainerColliderTag |  | A semantic [`ContainerColliderTag`](container_collider_tag.md) describing the semantic nature of the event. |

