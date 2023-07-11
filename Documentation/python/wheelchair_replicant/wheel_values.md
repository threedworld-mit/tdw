# WheelValues

`from wheelchair_replicant.wheel_values import WheelValues`

Wheel values for a move or turn action.

***

## Fields

- `brake_at` The distance or angle at which to start braking.

- `brake_torque` The torque that will be applied to the rear wheels at the end of the action.

- `left_motor_torque` The torque that will be applied to the left rear wheel at the start of the action.

- `right_motor_torque` The torque that will be applied to the right rear wheel at the start of the action.

- `steer_angle` The steer angle in degrees that will applied to the front wheels at the start of the action.

***

## Functions

#### \_\_init\_\_

**`WheelValues(brake_at, brake_torque, left_motor_torque, right_motor_torque, steer_angle)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| brake_at |  float |  | The distance or angle at which to start braking. |
| brake_torque |  float |  | The torque that will be applied to the rear wheels at the end of the action. |
| left_motor_torque |  float |  | The torque that will be applied to the left rear wheel at the start of the action. |
| right_motor_torque |  float |  | The torque that will be applied to the right rear wheel at the start of the action. |
| steer_angle |  float |  | The steer angle in degrees that will applied to the front wheels at the start of the action. |

#### get_default_values

**`self.get_default_values()`**

_Returns:_  Wheel values, all set at 0.

#### get_turn_values

**`self.get_turn_values(angle, arrived_at)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| angle |  float |  | The target angle in degrees. |
| arrived_at |  float |  | The arrived-at threshold in degrees. |

_Returns:_  Wheel values for a turn action.

#### get_move_values

**`self.get_move_values(distance)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| distance |  float |  | The target distance in meters. |

_Returns:_  Wheel values for a move action.

