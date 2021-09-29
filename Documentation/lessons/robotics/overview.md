##### Robotics

# Overview

TDW includes a full robotics API. You can add robots to a scene and either set target angles or positions for their joints, or apply forces and torques.

This tutorial will cover how to add and control robots in TDW using a higher-level API (the `Robot` add-on) and lower-level API commands.

Robots are agents but are *not* [avatars](../core_concepts/avatars.md) in TDW. Avatar commands won't work with robots.

![](images/overview/ur5.gif)

## High-level API: `magnebot`

[`magnebot`](https://github.com/alters-mit/magnebot) is a high-level robotics-like API. A Magnebot agent isn't strictly speaking a robot but it does use robotics commands. The Magnebot API has a simplified frontend API. For example, to add a Magnebot to a scene and move the Magnebot forward by 2 meters:

```python
from magnebot import MagnebotController

c = MagnebotController()
c.init_scene()
c.move_by(2)
```

![](images/overview/reach_high.gif)

***

**Next: [The `Robot` add-on](robot_add_on.md)**

[Return to the README](../../../README.md)

***

High-level API:

- [`magnebot`](https://github.com/alters-mit/magnebot)