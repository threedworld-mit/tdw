##### Semantic States

# Grasped

*If you haven't done so already, please read the overview documentation for [TDW agents](../agents/overview.md) as well as the documentation for the particular type of agent that you want to use.*

## Agents and grasp states

Certain types of agents can grasp objects. In some cases, "grasped" is an explicitly-defined semantic state and in other cases it is not:

- A [Robot](../robots/overview.md) does *not* have an explicitly-defined "grasp" state because robots are driven purely by the physics simulation. You will need to define the state at which an end effector is "grasping" an object.
- A [Magnebot](https://github.com/alters-mit/magnebot) has an explicitly-defined  "grasp" state; [read this for more information](https://github.com/alters-mit/magnebot/blob/main/doc/manual/magnebot/grasp.md).
- A [VR agents](../vr/overview.md) has an explicitly-define "grasp" state. Each VR rig add-on has a `held_left` and a `held_right` field. These are lists of object IDs held by each hand.

## Objects contained by grasped objects

None of these agents have explicit semantic states for held objects that contain other objects. For example, if the agent is holding a basket and there is a ball in the basket, there is no way for the agent's code to know that the agent is also holding the ball. In cases like this, you'll need to check for [containment](containment.md).

***

**This is the last document in the "Semantic States" tutorial.**

[Return to the README](../../../README.md)

