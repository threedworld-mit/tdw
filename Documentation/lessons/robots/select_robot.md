##### Robots

# Select a robot

Robots are handled in TDW very similarly to [objects](../core_concepts/objects.md). The robots are asset bundles stored on a remote S3 server. There is a corresponding [`RobotLibrarian`](../../python/librarian/robot_librarian.md) collection of metadata records.

This will print the name of each robot that is included by default in TDW:

```python
from tdw.librarian import RobotLibrarian

lib = RobotLibrarian()
for record in lib.records:
    print(record.name)
```

Output *(this will change as more robots are added to TDW)*:

```
baxter
fetch
niryo_one
sawyer
shadowhand
ur10
ur3
ur5
```

To select a robot, simply set the `name` field in the [`Robot`](../../python/add_ons/robot.md) constructor to a valid robot:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot

c = Controller()
robot_id = c.get_unique_id()
robot = Robot(name="baxter",
              robot_id=robot_id)
c.add_ons.append(robot)
c.communicate(TDWUtils.create_empty_room(12, 12))
c.communicate({"$type": "terminate"})
```

***

**Next: [Add your own robots to TDW](custom_robots.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`RobotLibrarian`](../../python/librarian/robot_librarian.md)
- [`Robot`](../../python/add_ons/robot.md)

