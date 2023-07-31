# WindSource

`from tdw.obi_data.wind_source import WindSource`

A source of wind: An invisible Obi fluid that can dynamically adjust its rotation, speed, etc.

***

## Fields

- `wind_id` The ID of this wind source.

***

## Functions

#### \_\_init\_\_

**`WindSource(wind_id, position, rotation)`**

**`WindSource(wind_id, position, rotation, capacity=2000, speed=1, lifespan=0.5, smoothing=0.5, resolution=1, vorticity=0.5, random_velocity=0.125, minimum_pool_size=0.5, visible=False, emitter_radius=0.25, solver_id=0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wind_id |  int |  | The ID of this wind source. |
| position |  POSITION |  | The position of the wind source. |
| rotation |  ROTATION |  | The rotation of the wind in Euler angles. |
| capacity |  int  | 2000 | The maximum amount of emitted particles. |
| speed |  float  | 1 | The emission speed in meters per second. |
| lifespan |  float  | 0.5 | The particle lifespan in seconds. A higher lifespan will result in "gustier" wind because particles will linger in the scene and prevent new particles from being created. |
| smoothing |  float  | 0.5 | A percentage of the particle radius used to define the radius of the zone around each particle when calculating fluid density. A lower value will create a more scattered fluid. |
| resolution |  float  | 1 | The size and amount of particles in 1 cubic meter. A value of 1 will use 1000 particles per cubic meter. For larger wind sources, consider lowering this value. |
| vorticity |  float  | 0.5 | Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5. This will increase turbulence, although the difference is relatively minor. |
| random_velocity |  float  | 0.125 | The maximum random speed in meters per second that can be applied to a particle. This will increase turbulence. |
| minimum_pool_size |  float  | 0.5 | The minimum amount of inactive particles available before the emitter is allowed to resume emission. |
| visible |  bool  | False | If True, make the fluid visible. This is useful for debugging. |
| emitter_radius |  float  | 0.25 | The radius of the wind source. |
| solver_id |  int  | 0 | The ID of the Obi solver. |

#### set_speed

**`self.set_speed(speed, ds)`**

Set a target wind speed.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| speed |  float |  | The target speed in meters per second. |
| ds |  float |  | The current speed will increase/decrease by this delta per `communicate()` call until it is at the target. |

#### get_speed

**`self.get_speed()`**

_Returns:_  The current wind speed.

#### is_accelerating

**`self.is_accelerating()`**

_Returns:_  True if the speed is accelerating or decelerating.

#### set_gustiness

**`self.set_gustiness(capacity, dc, lifespan, dl)`**

Set the "gustiness" of the wind i.e. the duration of pauses between emitted particles.

This tends to "override" the wind speed, which merely controls the velocity of particles in the scene.

The resulting gusts will always be periodic. If you want gusts to be more random, call this function with different values every *n* `communicate()` calls.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| capacity |  int |  | The target maximum number of particles. A higher particle count will create a steadier stream of particles but can significantly impact simulation performance. |
| dc |  int |  | The current capacity will increase/decrease by this delta per `communicate()` call until it is at the target. |
| lifespan |  float |  | The particle lifespan in seconds. A higher lifespan will result in "gustier" wind because particles will linger in the scene and prevent new particles from being created. |
| dl |  float |  | The current lifespan will increase/decrease by this delta per `communicate()` call until it is at the target. |

#### is_gusting

**`self.is_gusting()`**

_Returns:_  Tuple: True if we're at the target capacity, True if we're at the target lifespan.

#### set_spread

**`self.set_spread(smoothing, ds, resolution, dr)`**

Set how far the wind fluid can spread.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| smoothing |  float |  | A percentage of the particle radius used to define the radius of the zone around each particle when calculating fluid density. A lower value will create a more scattered fluid. |
| ds |  float |  | The current smoothing will increase/decrease by this delta per `communicate()` call until it is at the target. |
| resolution |  float |  | The size and amount of particles in 1 cubic meter. A value of 1 will use 1000 particles per cubic meter. For larger wind sources, consider lowering this value. |
| dr |  float |  | The current resolution will increase/decrease by this delta per `communicate()` call until it is at the target. |

#### is_spreading

**`self.is_spreading()`**

_Returns:_  Tuple: True if the smoothing value is at the target, True if the resolution value is at the target.

#### set_turbulence

**`self.set_turbulence(vorticity, dv, random_velocity, dr)`**

Set the wind turbulence.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| vorticity |  float |  | Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5. This will increase turbulence, although the difference is relatively minor. |
| dv |  float |  | The current vorticity will increase/decrease by this delta per `communicate()` call until it is at the target. |
| random_velocity |  float |  | The maximum random speed in meters per second that can be applied to a particle. This will increase turbulence. |
| dr |  float |  | The current random velocity will increase/decrease by this delta per `communicate()` call until it is at the target. |

#### is_turbulating

**`self.is_turbulating()`**

_Returns:_  Tuple: True if the vorticity value is at the target, True if the random velocity value is at the target.

#### move_to

**`self.move_to(position, dp)`**

Start moving to the target position.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  POSITION |  | The new position. |
| dp |  float |  | Move this many meters per `communicate()` call. |

#### get_position

**`self.get_position()`**

_Returns:_  The position of the wind source.

#### is_moving

**`self.is_moving()`**

_Returns:_  True if the wind source is moving.

#### rotate_by

**`self.rotate_by(angle, da)`**

**`self.rotate_by(angle, da, axis="yaw")`**

Rotate the wind fluid emitter with an angle and an axis.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| angle |  float |  | The target angle in degrees. |
| da |  float |  | Increment `angle` by this many degrees per `communicate()` call. |
| axis |  str  | "yaw" | The axis of rotation: `"pitch"`, `"yaw"`, or `"roll"`. |

#### get_rotation

**`self.get_rotation()`**

_Returns:_  Tuple: The angle of rotation in degrees, the axis of rotation.

#### is_rotating

**`self.is_rotating()`**

_Returns:_  True if the wind source is rotating.

#### update

**`self.update()`**

Don't call this in your controller. This is called internally by the `Obi` add-on.

Update the wind. Create the fluid actor if it doesn't exist. Lerp all values that need lerping.

_Returns:_  A list of commands.

