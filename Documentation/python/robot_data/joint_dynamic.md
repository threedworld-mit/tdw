# JointDynamic

`from tdw.robot_data.joint_dynamic import JointDynamic`

Dynamic info for a joint that can change per-frame, such as its current position.

***

## Fields

- `joint_id` The ID of this joint.

- `position` The worldspace position of this joint as an `[x, y, z]` numpy array.

- `angles` The angles of each axis of the joint in degrees. For prismatic joints, you need to convert this from degrees to radians in order to get the correct distance in meters.

- `moving` If True, this joint is currently moving.

***

## Functions

#### \_\_init\_\_

**`JointDynamic(joint_id, position, angles, moving)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| joint_id |  int |  | The ID of this joint. |
| position |  np.array |  | The worldspace position of this joint as an `[x, y, z]` numpy array. |
| angles |  np.array |  | The angles of each axis of the joint in degrees as a numpy array. For prismatic joints, you need to convert this from degrees to radians in order to get the correct distance in meters. |
| moving |  bool |  | If True, this joint is currently moving. |

