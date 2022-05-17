# ContainmentEvent

`from tdw.container_data.containment_event import ContainmentEvent`

Data describing a containment event i.e. when a container shape overlaps with one or more objects.

***

## Fields

- `container_id` The ID of the container.

- `object_ids` The IDs of the contained objects as a numpy array

- `tag` A semantic [`ContainerTag`](container_tag.md) describing the semantic nature of the event.

***

## Functions

#### \_\_init\_\_

**`ContainmentEvent(container_id, object_ids, tag)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| container_id |  int |  | The ID of the container. |
| object_ids |  np.array |  | The IDs of the contained objects as a numpy array. |
| tag |  ContainerTag |  | A semantic [`ContainerTag`](container_tag.md) describing the semantic nature of the event. |

