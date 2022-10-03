# LisdfRobotMetadata

`from tdw.lisdf_data.lisdf_robot_metadata import LisdfRobotMetadata`

Metadata for how to add a robot from a .urdf file referenced by a .lisdf file.
This will create a "fixed" version of a .urdf file that includes simplified namespaces, removed links, etc.

***

## Fields

- `name` The name of the robot.

- `link_name_excludes_regex` A list of regular expressions to search for in links, for example `["_gazebo_"]`. Link names that match this will be removed.

- `link_exclude_types` Some links have a `type` attribute. Exclude links matching this types in this list, for example `["laser", "camera"]`.

***

## Functions

#### \_\_init\_\_

**`LisdfRobotMetadata(name)`**

**`LisdfRobotMetadata(name, link_name_excludes_regex=None, link_exclude_types=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the robot. |
| link_name_excludes_regex |  List[str] | None | A list of regular expressions to search for in links, for example `["_gazebo_"]`. Link names that match this will be removed. |
| link_exclude_types |  List[str] | None | Some links have a `type` attribute. Exclude links matching this types in this list, for example `["laser", "camera"]`. |

