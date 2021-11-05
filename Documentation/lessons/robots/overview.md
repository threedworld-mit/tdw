##### Robots

# Overview

*Robots in TDW is handled via the PhysX physics engine. If you haven't done so already, we strongly recommend you read the [physics tutorial](../physx/overview.md).*

TDW includes a full robotics API. You can add robots to a scene and either set target angles or positions for their joints, or apply forces and torques.

This tutorial will cover how to add and control robots in TDW using a higher-level API (the `Robot` add-on) and lower-level API commands.

Robots are agents but are *not* [avatars](../core_concepts/avatars.md) in TDW. Avatar commands won't work with robots.

![](images/overview/ur5.gif)

***

**Next: [The `Robot` add-on](robot_add_on.md)**

[Return to the README](../../../README.md)