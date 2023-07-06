##### Wheelchair Replicants

# Overview

A **Wheelchair Replicant** is a wheelchair-bound human-like [agent](../agents/overview.md). 

A Wheelchair Replicant moves and turns by applying torques and steering angles to its wheels. A Wheelchair Replicant can look at or reach for objects using inverse kinematics (IK).

![](images/move_grasp_drop.gif)

## The `WheelchairReplicant` add-on

WheelchairReplicants are best controlled via the [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md) add-on. Like all other add-ons, the `WheelchairReplicant` add-on decomposes into low-level TDW commands but, given the complexity of the agent, we recommend that you *always* use the `WheelchairReplicant` add-on rather than directly manipulating the agent with low-level commands.

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

## Differences between Wheelchair Replicants and Replicants

The Replicant and Wheelchair Replicant are very similar. In many cases, they share the same code; the add-ons themselves are subclasses of the same [`ReplicantBase`](../../python/add_ons/replicant_base.md) abstract class. There are some important differences, however, especially in how Replicants and Wheelchair Replicants move and turn.

**Each document in this lesson will have a "Differences between Wheelchair Replicants and Replicants" section to compare the two agents.** 

## Differences between  Wheelchair Replicants and Robots

Wheelchair Replicants are similar to [robots](../robots/overview.md)  in that they can induce and respond to physics events, and that they move by applying forces to their wheels.  Like robots, Wheelchair Replicants are agents but are *not* [avatars](../core_concepts/avatars.md) in TDW. Avatar commands won't work with Wheelchair Replicants. Wheelchair Replicants differ from robots in three key ways:

1. Robots articulate their arms by applying forces to each joint. Wheelchair Replicants move their arms via inverse kinematics (IK), thus making their arm articulation less realistic than robots (albeit significantly easier to use).
2. Wheelchair Replicants don't have a realistic grasping mechanic.
3. Wheelchair Replicants use different Unity components than Robots, resulting in simulated movement that is more suitable for the hybrid nature of the physically-driven wheelchair and the IK-driven arms. At a high level, this means that Wheelchair Replicants and Robots require different types of output data and the add-ons therefore need to be structured in different ways.

## Wheelchair Replicant asset bundles

Like [objects](../core_concepts/objects.md) and [scenes](../core_concepts/scenes.md), and Replicants, Wheelchair Replicants are **asset bundles** stored on a remote S3 server that must be downloaded before they can be added to the scene. This means that when you first add a Wheelchair Replicant to the scene, there will be a brief pause while it is downloaded and loaded into memory. For subsequent scene resets, the Wheelchair Replicant will already in memory and will appear immediately.

Like all other asset bundle types in TDW, Replicants have metadata records stored in the TDW Python module. Each Replicant has a corresponding [`HumanoidRecord`](../../python/librarian/humanoid_librarian.md), which is stored in a [`HumanoidLibrarian`](../../python/librarian/humanoid_librarian.md). To print the name of each available Wheelchair Replicant:

```python
from tdw.librarian import HumanoidLibrarian

library = HumanoidLibrarian("wheelchair_replicants.json")
for record in library.records:
    print(record.name)
```

***

**Next: [Actions](actions.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md)
- [`Replicant`](../../python/add_ons/replicant.md)
- [`ReplicantBase`](../../python/add_ons/replicant_base.md)