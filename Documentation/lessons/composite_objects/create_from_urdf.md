##### Composite (articulated) objects

# Create a composite object from a .urdf file

Assuming that a composite object only has articulated joints (in other words, it doesn't have lights or other non-joints), the object can be expressed in a .urdf file.

It is possible to create composite objects from a .urdf file, but usually not advisable. This is a backend document for such special cases.

## Composite objects and robots

Given that a .urdf file can describe a composite object, it follows that technically any robot *can* be a TDW composite object. However, **in TDW, robots and composites are not the same.** [Robots](../robots/overview.md) use ArticulationBody components for joints. Composite objects use Joint components. 

There are advantages and disadvantages to each of these but generally if you're creating a robot asset bundle, you should *always* use [RobotCreator](../robots/custom_robots.md) and if you're creating an articulated object from a .urdf file, you can use the CompositeObjectCreator.

## The `CompositeObjectCreator`

[`CompositeObjectCreator`](../../python/asset_bundle_creator/composite_object_creator.md) can be used to create asset bundles *from a .urdf file.* If you want to create an asset bundle from a .fbx file or a prefab, *do not* use `CompositeObjectCreator`; use `ModelCreator` instead, [as described here](create_from_prefab.md).

The syntax for `CompositeObjectCreator` is very similar to that of `ModelCreator`, except that the source file is a .urdf file instead of a .fbx or .obj file:

```python
from pathlib import Path
from tdw.asset_bundle_creator.composite_object_creator import CompositeObjectCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_file = Path.home().joinpath("partnet_mobility/Basin/102379/mobility.urdf")
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("custom_composite_object")
c = CompositeObjectCreator()
c.source_file_to_asset_bundles(name="basin_102379",
                               source_file=source_file,
                               output_directory=output_directory)
```

There are other API calls as well, some of which are shared with `ModelCreator`. [Read the API documentation here.](../../python/asset_bundle_creator/composite_object_creator.md)

***

**This is the last document in the "Composite (articulated) objects" tutorial.**

[Return to the README](../../../README.md)

***

Python API:

- [`CompositeObjectCreator`](../../python/asset_bundle_creator/composite_object_creator.md)
- [`RobotCreator`](../../python/asset_bundle_creator/robot_creator.md)

