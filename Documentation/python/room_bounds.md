# RoomBounds

`from scene.room_bounds import RoomBounds`

Data for the bounds of a room in a scene.

***

## Fields

- `room_id` The ID of the room.

- `center` The center of the room.

- `bounds` The bounds of the room.

- `x_min` Minimum x positional coordinate of the room.

- `y_min` Minimum y positional coordinate of the room.

- `z_min` Minimum z positional coordinate of the room.

- `x_max` Maximum x positional coordinate of the room.

- `y_max` Maximum y positional coordinate of the room.

- `z_max` Maximum z positional coordinate of the room.

***

## Functions

#### \_\_init\_\_

**`RoomBounds(env, i)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| env |  Environments |  | The environments output data. |
| i |  int |  | The index of this scene in env.get_num() |

#### is_inside

**`self.is_inside(x, z)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| x |  float |  | The x coordinate. |
| z |  float |  | The z coordinate. |

_Returns:_  True if position (x, z) is in the scene.

