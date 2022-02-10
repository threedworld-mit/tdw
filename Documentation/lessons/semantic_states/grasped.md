##### Semantic States

# Grasped

*If you haven't done so already, please read the overview documentation for [TDW agents](../agents/overview.md) as well as the documentation for the particular type of agent that you want to use.*

Certain types of agents can grasp objects. In some cases, "grasped" is an explicitly-defined semantic state and in other cases it is not:

- [Robots](../robots/overview.md) do *not* have an explicitly-defined "grasp" state because they are a purely physics-driven simulation. As in any other robotics simulation, you will need to define the state at which an end effector is "grasping" an object.
- [Magnebots](https://github.com/alters-mit/magnebot) have an explicitly-defined  "grasp" state; [read this for more information](https://github.com/alters-mit/magnebot/blob/main/doc/manual/magnebot/grasp.md).
- **TODO VR agents**

***

**This is the last document in the "Semantic States" tutorial.**

[Return to the README](../../../README.md)

