# Drive

`from tdw.robot_data.drive import Drive`

Static data for a joint drive.

***

## Fields

- `axis` The axis of rotation. Can be `"x"`, `"y"`, or `"z"`.

- `limits` Tuple: The lower and upper limits of the drive rotation in degrees.

- `force_limit` The limit of how much force can be applied to the drive.

- `damping` The damping value.

- `stiffness` The stiffness value.

***

## Functions

#### \_\_init\_\_

**`Drive(sr, joint_index, drive_index)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| sr |  StaticRobot |  | The StaticRobot output data. |
| joint_index |  int |  | The index of the joint in the output data that this drive belongs to. |
| drive_index |  int |  | The index of this drive in the joint data. |

