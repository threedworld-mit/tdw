# RobotArm

`from tdw.add_ons.robot_arm import RobotArm`

A robot with a single arm.
This class includes an inverse kinematic (IK) solver that allows the robot to reach for a target position.

***

## Fields

- `static` [Static robot data.](../robot_data/robot_static.md)

- `dynamic` [Dynamic robot data.](../robot_data/robot_dynamic.md)

- `name` The name of the robot.

- `url` The URL or filepath of the robot asset bundle.

***

## Functions

#### \_\_init\_\_

**`RobotArm(name)`**

**`RobotArm(name, robot_id=0, position=None, rotation=None, source=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the robot. |
| robot_id |  int  | 0 | The ID of the robot. |
| position |  Dict[str, float] | None | The position of the robot. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The rotation of the robot in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| source |  Union[RobotLibrarian, RobotRecord] | None | The source file of the robot. If None: The source will be the URL of the robot record in TDW's built-in [`RobotLibrarian`](../librarian/robot_librarian.md). If `RobotRecord`: the source is the URL in the record. If `RobotLibrarian`: The source is the record in the provided `RobotLibrarian` that matches `name`. |

#### reach_for

**`self.reach_for(target)`**

Start to reach for a target position.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| target |  Union[Dict[str, float] |  | The target position. Can be a dictionary or a numpy array. |

#### set_joint_targets

**`self.set_joint_targets(targets)`**

Set target angles or positions for a dictionary of joints.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| targets |  Dict[int, Union[float, Dict[str, float] |  | A dictionary of joint targets. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (angles in degrees). For revolute joints, this must be a float (an angle in degrees). For prismatic joints, this must be a float (a distance in meters). |

#### add_joint_forces

**`self.add_joint_forces(forces)`**

Add torques and forces to a dictionary of joints.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| forces |  Dict[int, Union[float, Dict[str, float] |  | A dictionary of joint forces. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (torques in Newtons). For revolute joints, this must be a float (a torque in Newtons). For prismatic joints, this must be a float (a force in Newtons). |

#### stop_joints

**`self.stop_joints()`**

**`self.stop_joints(joint_ids=None)`**

Stop the joints at their current angles or positions.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| joint_ids |  List[int] | None | A list of joint IDs. If None, stop all joints. |

#### add_joint_forces

**`self.add_joint_forces(forces)`**

Add torques and forces to a dictionary of joints.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| forces |  Dict[int, Union[float, Dict[str, float] |  | A dictionary of joint forces. Key = The ID of the joint. Value = the targets. For spherical joints, this must be a Vector3 dictionary, for example `{"x": 40, "y": 0, "z": 0}` (torques in Newtons). For revolute joints, this must be a float (a torque in Newtons). For prismatic joints, this must be a float (a force in Newtons). |

