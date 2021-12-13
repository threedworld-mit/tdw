# JointStatic

`from tdw.robot_data.joint_static import JointStatic`

Static robot joint data.

***

## Fields

- `joint_id` The ID of this joint.

- `name` The name of the joint.

- `joint_type` [The type of joint.](joint_type.md)

- `segmentation_color` The segmentation color of this joint as an `[r, g, b]` numpy array.

- `mass` The mass of this joint.

- `immovable` If True, this joint is immovable.

- `root` If True, this is the root joint.

- `parent_id` The ID of this joint's parent joint. Ignore if `self.root == True`.

- `drives` A dictionary of [Drive data](drive.md) for each of the robot's joints. Key = The drive axis (`"x"`, `"y"`, or `"z"`).

***

## Functions

#### \_\_init\_\_

**`JointStatic(static_robot, joint_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| static_robot |  StaticRobot |  | Static robot output data from the build. |
| joint_index |  int |  | The index of this joint in the list of joints. |

