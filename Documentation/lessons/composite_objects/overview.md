##### Composite (articulated) objects

# Overview

*Composite objects utilize the PhysX physics engine. If you haven't done so already, please read [the documentation for PhysX in TDW](../physx/physx.md)*.

**Composite objects** are objects in TDW that have multiple "sub-objects". Sub-objects appear in [output data](../core_concepts/output_data.md) as separate objects with separate IDs and [segmentation colors](../visual_perception/id.md).

In most cases, composite objects are synonymous with "articulated objects" in that the sub-objects are articulated joints. However, this is not *always* the case. Composite objects can be:

- Objects with hinged joints such as a fridge with doors
- Objects with hinged motorized joints such as a fan
- Multiple disconnected objects such as a pot with a lid 
- An object with a light source such as a lamp

This lesson explains how to add and use composite objects in TDW and how to create custom composite objects. In general, creating composite objects requires a lot more knowledge of Unity Editor than [creating non-articulated, non-composite objects](../3d_models/custom_models.md); accordingly, the documentation for creating composite objects assumes more prior Unity Editor knowledge.

***

**Next: [How to use composite objects](composite_objects.md)**

[Return to the README](../../../README.md)
