# Drone

`from tdw.add_ons.drone import Drone`

A drone is a flying agent. From this API, you can set the drone's speed (lift, drive, turn) and turn its motor on and off.

The drone's output data, including images, is stored in [`drone.dynamic`](../drone/drone_dynamic.md).

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `LIBRARY_NAME` | str | The drone's library file. You can override this to use a custom library (e.g. a local library). | `"drones.json"` |

***

## Fields

- `initial_position` The initial position of the drone.

- `initial_rotation` The initial rotation of the drone in Euler angles.

- `dynamic` The [`DroneDynamic`](../drone/drone_dynamic.md) data.

- `drone_id` The ID of this drone.

- `avatar_id` The ID of the drone's avatar (camera). This is used internally for API calls.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Drone()`**

**`Drone(drone_id=0, position=None, rotation=None, name="drone", forward_speed=3, backward_speed=3, rise_speed=3, drop_speed=3, acceleration=0.3, deceleration=0.2, stability=0.1, turn_sensitivity=2, enable_lights=False, motor_on=True, image_capture=True, image_passes=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| drone_id |  int  | 0 | The ID of the drone. |
| position |  POSITION  | None | The position of the drone as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  ROTATION  | None | The rotation of the drone in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| name |  str  | "drone" | The name of the drone model. |
| forward_speed |  float  | 3 | Sets the drone's max forward speed. |
| backward_speed |  float  | 3 | Sets the drone's max backward speed. |
| rise_speed |  float  | 3 | Sets the drone's max vertical rise speed. |
| drop_speed |  float  | 3 | Sets the drone's max vertical drop speed. |
| acceleration |  float  | 0.3 | How fast the drone speeds up. |
| deceleration |  float  | 0.2 | How fast the drone slows down. |
| stability |  float  | 0.1 | How easily the drone is affected by outside forces. |
| turn_sensitivity |  float  | 2 | The name of the drone model. |
| enable_lights |  bool  | False | Sets whether or not the drone's lights are on. |
| motor_on |  bool  | True | Sets whether or not the drone is active on start. |
| image_capture |  bool  | True | If True, the drone will receive image and camera matrix data per `communicate()` call. Whether or not this is True, the drone will always render images in the simulation window. |
| image_passes |  List[str] | None | A list of image passes that will be captured. Ignored if `image_capture == False`. If None, defaults to `["_img", "_id"]`. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### set_lift

**`self.set_lift(lift)`**

Set the drone's lift force.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| lift |  int |  | The lift force. Must be -1, 0, or 1. |

#### set_drive

**`self.set_drive(drive)`**

Set the drone's drive force.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| drive |  int |  | The drive force. Must be -1, 0, or 1. |

#### set_turn

**`self.set_turn(turn)`**

Set the drone's turn force.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| turn |  int |  | The turn force. Must be -1, 0, or 1. |

#### set_motor

**`self.set_motor(motor_on)`**

Turn the drone's motor on or off.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| motor_on |  bool |  | If True, turn the motor on. If False, turn the motor off. |