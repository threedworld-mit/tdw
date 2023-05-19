# Vehicle

`from tdw.add_ons.vehicle import Vehicle`

A vehicle is a driving agent such as a car, bus or truck. From this API, you can set the vehicles's speed (rive, turn, brake) and turn its motor on and off.

The vehicle's output data, including images, is stored in [`vehicle.dynamic`](../vehicle/vehicle_dynamic.md).

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `LIBRARY_NAME` | str | The vehicle's library file. You can override this to use a custom library (e.g. a local library). | `"vehicles.json"` |

***

## Fields

- `initial_position` The initial position of the vehicle.

- `dynamic` The initial rotation of the vehicle in Euler angles.

- `vehicle_id` The ID of this vehicle.

- `avatar_id` The ID of the vehicle's avatar (camera). This is used internally for API calls.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Vehicle(position, rotation)`**

**`Vehicle(vehicle_id=0, position, rotation, name="all_terrain_vehicle", forward_speed=30, reverse_speed=12, image_capture=True, image_passes=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| vehicle_id |  int  | 0 | The ID of the vehicle. |
| position |  Union[Dict[str, float] |  | The position of the vehicle as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Union[Dict[str, float] |  | The rotation of the vehicle in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| name |  str  | "all_terrain_vehicle" | The name of the vehicle model. |
| forward_speed |  float  | 30 | Sets the vehicle's max forward speed. |
| reverse_speed |  float  | 12 | Sets the vehicle's max reverse speed. |
| image_capture |  bool  | True | If True, the vehicle will receive image and camera matrix data per `communicate()` call. Whether or not this is True, the vehicle will always render images in the simulation window. |
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

#### set_drive

**`self.set_drive(drive)`**

Set the vehicle's drive force.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| drive |  int |  | The drive force. Must be -1, 0, or 1. |

#### set_turn

**`self.set_turn(turn)`**

Set the vehicle's turn force.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| turn |  int |  | The turn force. Must be -1, 0, or 1. |