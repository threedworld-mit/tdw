##### Wheelchair Replicants

# Overview

A **Wheelchair Replicant** is a wheelchair-bound human-like [agent](../agents/overview.md). 

A Wheelchair Replicant moves and turns by applying torques and steering angles to its wheels. A Wheelchair Replicant can look at or reach for objects using inverse kinematics (IK).

![](images/move_grasp_drop.gif)

## Wheelchair Replicants and Robots

Wheelchair Replicants differ from [robots](../robots/overview.md) in that they aren't *entirely* physics-driven. In addition  to being massless, Wheelchair  Replicant joints aren't defined as motorized drives. Joint velocity, momentum, etc. aren't concepts that exist in the context of a Wheelchair  Replicant.

Wheelchair  Replicants are thus a compromise on realism: It is far easier to achieve complex behavior with a Wheelchair  Replicant than with a robot. On the other hand, the Wheelchair  Replicant's motion itself isn't driven by physics to the extent that a robot's would be.

Like robots, Wheelchair Replicants are agents but are *not* [avatars](../core_concepts/avatars.md) in TDW. Avatar commands won't work with Wheelchair Replicants.

## Wheelchair Replicants and Replicants

The Replicant and Wheelchair Replicant have nearly the same action space APIs, though there are some important differences. For the sake of describing Wheelchair Replicants, it can be helpful to compare to them to Replicants. 

- A Replicant is often used as an "able-bodied" agent, but it is actually more flexible than that. A Replicant can walking with a limping animation, for example. Or, the controller can constrain which objects it can grasp by mass, thus making the Replicant "weak". Or, the Replicant can ignore its image output data, thus becoming "blind". The last two examples, as well as many others, are just as applicable to a Wheelchair Replicant. The primary difference between the two agent types is their means of locomotion:

  - A Replicant moves via a looping walk animation. This is pseduo-physical behavior because the Replicant is kinematic. For more information, [read this](../replicants/movement.md).

  - A Wheelchair Replicant moves by applying torques and steering angles to its wheels. It is thus much more physically-driven than a Replicant. For more information, [read this](movement.md).
- Wheelchair Replicant can't be [animated with pre-recorded animations](../replicants/animations.md).
- The Replicant and Wheelchair Replicant arm articulation APIs are nearly the same. The arm motions are somewhat different because the Wheelchair Replicant uses a different IK solver. Unlike the Replicant, a Wheelchair Replicant can't apply [IK plans](../replicants/arm_articulation_4.md).
- The Replicant and Wheelchair Replicant head rotation APIs are exactly the same.
- The Replicant and Wheelchair Replicant collision detection systems are exactly the same.

## The `WheelchairReplicant` add-on

Like robots and Replicants, WheelchairReplicants are best controlled via the [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md) add-on. Like all other add-ons, the `WheelchairReplicant` add-on decomposes into low-level TDW commands but, given the complexity of the agent, we recommend that you *always* use the `WheelchairReplicant` add-on rather than directly manipulating the agent with low-level commands.

Adding a Wheelchair Replicant to a scene is simple:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant

c = Controller()
replicant = WheelchairReplicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

You can set the initial position and rotation of the Replicant in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant

c = Controller()
replicant = WheelchairReplicant(position={"x": 1, "y": 0, "z": -2},
                                rotation={"x": 0, "y": 30, "z": 0})
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

There are additional constructor parameters that will be covered in subsequent documents.

## Wheelchair Replicant asset bundles

Wheelchair asset bundles are handled exactly the same way as Replicant asset bundles. [Read this for more information.](../replicants/overview.md) The only difference is that Wheelchair Replicant metadata records are stored in a different library: `wheelchair_replicants.json`.

***

**Next: [Actions](actions.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md)
- [`Replicant`](../../python/add_ons/replicant.md)