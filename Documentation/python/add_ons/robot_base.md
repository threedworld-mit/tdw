# RobotBase

`from tdw.add_ons.robot_base import RobotBase`

Abstract base class for robots.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `NON_MOVING` | float | If a joint has moved less than this many degrees (revolute or spherical) or meters (prismatic) since the previous frame, it is considered to be not moving for the purposes of determining which joints are moving. |

***

## Fields

- `initial_position` The initial position of the robot.

- `initial_rotation` The initial rotation of the robot.

- `robot_id` The ID of this robot.

- `static` Static robot data.

- `dynamic` Dynamic robot data.

***

## Functions

#### \_\_init\_\_

**`RobotBase()`**

**`RobotBase(robot_id=0, position=None, rotation=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| robot_id |  int  | 0 | The ID of the robot. |
| position |  Dict[str, float] | None | The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |

#### get_initialization_commands

**`self.get_initialization_commands(joint_ids)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| joint_ids |  |  | A list of joint IDs to check for movement. If `None`, check all joints for movement. |

_Returns:_  True if the joints are moving.

#### joints_are_moving

**`self.joints_are_moving()`**

**`self.joints_are_moving(joint_ids=None)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| joint_ids |  List[int] | None | A list of joint IDs to check for movement. If `None`, check all joints for movement. |

_Returns:_  True if the joints are moving.

#### on_send

**`self.on_send()`**

Mark this robot as being reset.

#### reset

**`self.reset()`**

Mark this robot as being reset.

