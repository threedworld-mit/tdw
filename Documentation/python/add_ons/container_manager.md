# ContainerManager

`from tdw.add_ons.container_manager import ContainerManager`

Manage containment events for 'container' objects.

'Containers' can be concave objects such as baskets but they don't have to be. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.

An object is 'contained' by a 'container' if it overlaps with a "containment" space, for example the interior of a pot.

***

## Fields

- `events` A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container shape ID (not the object ID). Value = A list of [`ContainmentEvent`](../container_data/containment_event.md) data.

- `container_shapes` A dictionary of container shape IDs. Key = The container shape ID. Value = The object ID.

- `tags` Tags describing each container shape. Key = The container shape ID. Value = [`ContainerTag`](../container_data/container_tag.md).

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ContainerManager()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### add_box

**`self.add_box(object_id, position, tag, half_extents, rotation)`**

Add a box container shape to an object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the object. |
| position |  Dict[str, float] |  | The position of the box relative to the parent object. |
| tag |  ContainerTag |  | The box's semantic [`ContainerTag`](../container_data/container_tag.md). |
| half_extents |  Dict[str, float] |  | The half-extents (half the scale) of the box. |
| rotation |  Dict[str, float] |  | The rotation of the box in Euler angles relative to the parent object. |

_Returns:_  The ID of the container shape.

#### add_cylinder

**`self.add_cylinder(object_id, position, tag, radius, height, rotation)`**

Add a cylinder container shape to an object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the object. |
| position |  Dict[str, float] |  | The position of the cylinder relative to the parent object. |
| tag |  ContainerTag |  | The cylinder's semantic [`ContainerTag`](../container_data/container_tag.md). |
| radius |  float |  | The radius of the cylinder. |
| height |  float |  | The height of the cylinder. |
| rotation |  Dict[str, float] |  | The rotation of the cylinder in Euler angles relative to the parent object. |

_Returns:_  The ID of the container shape.

#### add_sphere

**`self.add_sphere(object_id, position, tag, radius)`**

Add a sphere container shape to an object.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the object. |
| position |  Dict[str, float] |  | The position of the sphere relative to the parent object. |
| tag |  ContainerTag |  | The sphere's semantic [`ContainerTag`](../container_data/container_tag.md). |
| radius |  float |  | The radius of the sphere. |

_Returns:_  The ID of the container shape.

#### reset

**`self.reset()`**

Reset this add-on. Call this before resetting a scene.