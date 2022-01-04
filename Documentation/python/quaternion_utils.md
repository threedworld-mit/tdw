# QuaternionUtils

`from tdw.quaternion_utils import QuaternionUtils`

Helper functions for using quaternions.

Quaternions are always numpy arrays in the following order: `[x, y, z, w]`.
This is the order returned in all Output Data objects.

Vectors are always numpy arrays in the following order: `[x, y, z]`.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `UP ` |  | The global up directional vector. |
| `FORWARD` | np.array | The global forward directional vector. |
| `IDENTITY ` |  | The quaternion identity rotation. |

***

#### get_inverse

**`QuaternionUtils.get_inverse(q)`**

_This is a static function._

Source: https://referencesource.microsoft.com/#System.Numerics/System/Numerics/Quaternion.cs


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.array |  | The quaternion. |

_Returns:_  The inverse of the quaternion.

#### multiply

**`QuaternionUtils.multiply(q1, q2)`**

_This is a static function._

Multiply two quaternions.
Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q1 |  np.array |  | The first quaternion. |
| q2 |  np.array |  | The second quaternion. |

_Returns:_  The multiplied quaternion: `q1 * q2`

#### get_conjugate

**`QuaternionUtils.get_conjugate(q)`**

_This is a static function._

Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.array |  | The quaternion. |

_Returns:_  The conjugate of the quaternion: `[-x, -y, -z, w]`

#### multiply_by_vector

**`QuaternionUtils.multiply_by_vector(q, v)`**

_This is a static function._

Multiply a quaternion by a vector.
Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.array |  | The quaternion. |
| v |  np.array |  | The vector. |

_Returns:_  A directional vector calculated from: `q * v`

#### world_to_local_vector

**`QuaternionUtils.world_to_local_vector(position, origin, rotation)`**

_This is a static function._

Convert a vector position in absolute world coordinates to relative local coordinates.
Source: https://answers.unity.com/questions/601062/what-inversetransformpoint-does-need-explanation-p.html


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  np.array |  | The position vector in world coordinates. |
| origin |  np.array |  | The origin vector of the local space in world coordinates. |
| rotation |  np.array |  | The rotation quaternion of the local coordinate space. |

_Returns:_  `position` in local coordinates.

#### get_up_direction

**`QuaternionUtils.get_up_direction(q)`**

_This is a static function._


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.array |  | The rotation as a quaternion. |

_Returns:_  A directional vector corresponding to the "up" direction from the quaternion.

#### euler_angles_to_quaternion

**`QuaternionUtils.euler_angles_to_quaternion(euler)`**

_This is a static function._

Convert Euler angles to a quaternion.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| euler |  np.array |  | The Euler angles vector. |

_Returns:_  The quaternion representation of the Euler angles.

#### quaternion_to_euler_angles

**`QuaternionUtils.quaternion_to_euler_angles(quaternion)`**

_This is a static function._

Convert a quaternion to Euler angles.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quaternion |  np.array |  | A quaternion as a nump array. |

_Returns:_  The Euler angles representation of the quaternion.

#### get_y_angle

**`QuaternionUtils.get_y_angle(q1, q2)`**

_This is a static function._

Source: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q1 |  np.array |  | The first quaternion. |
| q2 |  np.array |  | The second quaternion. |

_Returns:_  The angle between the two quaternions in degrees around the y axis.

#### is_left_of

**`QuaternionUtils.is_left_of(origin, target, forward)`**

_This is a static function._


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| origin |  np.array |  | The origin position. |
| target |  np.array |  | The target position. |
| forward |  np.array |  | The forward directional vector. |

_Returns:_  True if `target` is to the left of `origin` by the `forward` vector; False if it's to the right.

