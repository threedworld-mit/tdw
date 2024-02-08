# QuaternionUtils

`from tdw.quaternion_utils import QuaternionUtils`

Helper functions for using quaternions.

Quaternions are always numpy arrays in the following order: `[x, y, z, w]`.

This is the same order as any quaternion found in TDW's output data, e.g. `Transforms.get_rotation(index)`.

Vectors are always numpy arrays in the following order: `[x, y, z]`.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `UP` | np.ndarray | The global up directional vector. | `np.array([0, 1, 0])` |
| `FORWARD` | np.ndarray | The global forward directional vector. | `np.array([0, 0, 1])` |
| `RIGHT` | np.ndarray | The global right directional vector. | `np.array([1, 0, 0])` |
| `IDENTITY` | np.ndarray | The quaternion identity rotation. | `np.array([0, 0, 0, 1])` |

***

## Functions

#### get_inverse

**`QuaternionUtils.get_inverse(q)`**

_(Static)_

Source: https://referencesource.microsoft.com/#System.Numerics/System/Numerics/Quaternion.cs


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.ndarray |  | The quaternion. |

_Returns:_  The inverse of the quaternion.

#### multiply

**`QuaternionUtils.multiply(q1, q2)`**

_(Static)_

Multiply two quaternions.

Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q1 |  np.ndarray |  | The first quaternion. |
| q2 |  np.ndarray |  | The second quaternion. |

_Returns:_  The multiplied quaternion: `q1 * q2`

#### get_conjugate

**`QuaternionUtils.get_conjugate(q)`**

_(Static)_

Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.ndarray |  | The quaternion. |

_Returns:_  The conjugate of the quaternion: `[-x, -y, -z, w]`

#### multiply_by_vector

**`QuaternionUtils.multiply_by_vector(q, v)`**

_(Static)_

Multiply a quaternion by a vector.

Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.ndarray |  | The quaternion. |
| v |  np.ndarray |  | The vector. |

_Returns:_  A directional vector calculated from: `q * v`

#### world_to_local_vector

**`QuaternionUtils.world_to_local_vector(position, origin, rotation)`**

_(Static)_

Convert a vector position in absolute world coordinates to relative local coordinates.

Source: https://answers.unity.com/questions/601062/what-inversetransformpoint-does-need-explanation-p.html


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  np.ndarray |  | The position vector in world coordinates. |
| origin |  np.ndarray |  | The origin vector of the local space in world coordinates. |
| rotation |  np.ndarray |  | The rotation quaternion of the local coordinate space. |

_Returns:_  `position` in local coordinates.

#### world_to_local_rotation

**`QuaternionUtils.world_to_local_rotation(world_rotation, local_coord_rotation)`**

_(Static)_

Convert a rotation in absolute world coordinates to relative local coordinates.

Source: https://discussions.unity.com/t/what-is-the-rotation-equivalent-of-inversetransformpoint/45386


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| world_rotation |  np.ndarray |  | The rotation vector in world coordinates that you want to convert to local coordinates. |
| local_coord_rotation |  np.ndarray |  | The rotation vector of the local coordinates in world coordinates. |

_Returns:_  `rotation` vector of world_rotation in local coordinates.

#### get_up_direction

**`QuaternionUtils.get_up_direction(q)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q |  np.ndarray |  | The rotation as a quaternion. |

_Returns:_  A directional vector corresponding to the "up" direction from the quaternion.

#### euler_angles_to_quaternion

**`QuaternionUtils.euler_angles_to_quaternion(euler)`**

_(Static)_

Convert Euler angles to a quaternion.

Source: https://pastebin.com/riRLRvch


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| euler |  np.ndarray |  | The Euler angles vector. |

_Returns:_  The quaternion representation of the Euler angles.

#### quaternion_to_euler_angles

**`QuaternionUtils.quaternion_to_euler_angles(quaternion)`**

_(Static)_

Convert a quaternion to Euler angles.

Source: https://stackoverflow.com/a/12122899


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quaternion |  np.ndarray |  | A quaternion as a nump array. |

_Returns:_  The Euler angles representation of the quaternion.

#### get_y_angle

**`QuaternionUtils.get_y_angle(q1, q2)`**

_(Static)_

Source: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| q1 |  np.ndarray |  | The first quaternion. |
| q2 |  np.ndarray |  | The second quaternion. |

_Returns:_  The angle between the two quaternions in degrees around the y axis.

#### is_left_of

**`QuaternionUtils.is_left_of(origin, target, forward)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| origin |  np.ndarray |  | The origin position. |
| target |  np.ndarray |  | The target position. |
| forward |  np.ndarray |  | The forward directional vector. |

_Returns:_  True if `target` is to the left of `origin` by the `forward` vector; False if it's to the right.

