##### Core Concepts

# Random Numbers

In nearly all cases in TDW, the controller handles random number generation, not the build. This document explain best practices for generating and handling random numbers.

## Object IDs

The most common need for random numbers is for [object IDs](objects.md). In this case, we recommend calling `Controller.get_unique_id()`. You can find examples of this throughout TDW's documentation.

## Floats (positions, colors, etc.)

You can generate random floats with the standard Python `random` module.

Alternatively, you can generate numbers from a numpy `RandomState`:

```python
import numpy as np

seed = 0
rng = np.random.RandomState(seed)
```

According to numpy's documentation, `RandomState` is deprecated, but it's useful in TDW because it's easy to *seed*. **If you use the same random see in a `RandomState`, it will generate the same numbers.** This can be useful if you ever need to re-create a scene setup or trial that involves random numbers.

This will always generate the same float:

```python
import numpy as np

seed = 0
rng = np.random.RandomState(seed)
f = rng.uniform(-1.0, 1.0)
```

 **In the above example, sending `f` in a command may generate an error.** This is because Python's `json` library can't serialize numpy value types or numpy arrays. To prevent this, always cast to a Python value type:

```python
import numpy as np

seed = 0
rng = np.random.RandomState(seed)
f = float(rng.uniform(-1.0, 1.0))
```

**However, if you change the order/quantity/etc. of random numbers, you will get different results even if you use the same seed.** The random seed marks the starting point of random number generation, not the actual sequence of numbers. If you generate two random integers and two random floats, and then you modify the controller to remove one of the integers, the two floats will be different even if you use the same seed.

## Segmentation colors

The build (not the controller) assigns random [segmentation colors](../visual_perception/id.md) to each object. This *can* be deterministic, provided your controller sends [`set_random`](../../api/command_api.md#set_random):

```python
from tdw.controller import Controller

c = Controller()
c.communicate({"$type": "set_random",
               "seed": 0})
```

When you call `Controller()`, it calls `communicate()` and sends a list of commands, among them being `set_random`. If you call `set_random` again, you can set the *build's* random seed, which works the same way as a Python `RandomState` (it is a starting point for random number generation).

The build's random number generator is used to assign segmentation colors. So, by setting the same random seed every time, you will get the same segmentation colors every time (provided you don't edit your controller to add/remove objects).

If you explicitly send a `set_random` command and log it with a [`Logger`](../read_write/logger.md), and then reload the log file with a [`LogPlayback`](../read_write/logger.md), the segmentation colors will be the same because the log includes the `set_random` command. 

## Joint IDs and composite sub-object IDs

The build assigns random IDs for [robot joints](../robots/overview.md) and [composite sub-objects](../composite_objects/overview.md). 

If you try to add a robot or composite object to the scene and [log the commands](../read_write/logger.md), you will get an error when you try to load the log with a `LogPlayback` because the build will generate different IDs.

However, if you include a `set_random` command at the start of your controller, then the `Logger` will record that command, and the `LogPlayback` will send it, and therefore the joint IDs will be the same as before.

## Example Controllers

In this example controller, we ran an initial controller and wrote a dictionary of the return segmentation colors, joint IDs, and composite sub-object IDs. The controller will create the same scene and assert that the returns colors and IDs match the precalculate colors and IDs. If the controller doesn't print anything, then it worked as expected:

```python
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.robot import Robot
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.logger import Logger
from tdw.tdw_utils import TDWUtils

joint_ids = {0: np.array([147, 157, 175]),
             1008269081: np.array([195, 94, 113]),
             2005789796: np.array([0, 154, 146]),
             1706746116: np.array([138, 76, 169]),
             1922776196: np.array([207, 131, 96]),
             216757113: np.array([177, 130, 222]),
             1704308182: np.array([185, 30, 134])}
object_ids = {1: np.array([199, 145, 100]),
              1755192844: np.array([216, 138, 133])}
c = Controller()
robot = Robot(name="ur5")
object_manager = ObjectManager()
logger = Logger(path="determinism_log.txt")
c.add_ons.extend([logger, robot, object_manager])
c.communicate([{"$type": "set_random",
                "seed": 0},
               TDWUtils.create_empty_room(6, 6),
               Controller.get_add_object(model_name="microwave_composite",
                                         object_id=1,
                                         position={"x": 2, "y": 0, "z": 0})])

for object_id in object_manager.objects_static:
    assert object_id in object_ids, f"Object ID not found: {object_id}"
    color = object_manager.objects_static[object_id].segmentation_color
    assert (color == object_ids[object_id]).all(), f"Bad segmentation color for object {object_id}: {color}"

for joint_id in robot.static.joints:
    joint = robot.static.joints[joint_id]
    assert joint_id in joint_ids, f"Joint ID not found: {joint_id}"
    color = joint.segmentation_color
    assert (color == joint_ids[joint_id]).all(), f"Bad segmentation color for joint {joint_id}: {color}"

c.communicate({"$type": "terminate"})
```

In this example controller, we'll load a log file, run it, and compare the [output data](output_data.md) to the precalculated colors and IDs. If the controller doesn't print anything, then it worked as expected:

```python
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.log_playback import LogPlayback
from tdw.output_data import OutputData, SegmentationColors, StaticRobot

"""
Load a log file generated by a variant of `determinism_rng.py`.

Assert that the joint IDs, sub-object IDs, and all segmentation colors are the same as what was logged.
"""

joint_ids = {0: np.array([147, 157, 175]),
             1008269081: np.array([195, 94, 113]),
             2005789796: np.array([0, 154, 146]),
             1706746116: np.array([138, 76, 169]),
             1922776196: np.array([207, 131, 96]),
             216757113: np.array([177, 130, 222]),
             1704308182: np.array([185, 30, 134])}
object_ids = {1: np.array([199, 145, 100]),
              1755192844: np.array([216, 138, 133])}
c = Controller()
playback = LogPlayback()
playback.load("determinism_log.txt")
c.add_ons.append(playback)
while len(playback.playback) > 0:
    resp = c.communicate([])
    for i in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[i])
        if r_id == "segm":
            segm = SegmentationColors(resp[i])
            for j in range(segm.get_num()):
                object_id = segm.get_object_id(j)
                color = segm.get_object_color(j)
                assert object_id in object_ids, f"Object ID not found: {object_id}"
                assert (color == object_ids[object_id]).all(), f"Bad segmentation color for object {object_id}: {color}"
        elif r_id == "srob":
            srob = StaticRobot(resp[i])
            for j in range(srob.get_num_joints()):
                joint_id = srob.get_joint_id(j)
                color = srob.get_joint_segmentation_color(j)
                assert joint_id in joint_ids, f"Joint ID not found: {joint_id}"
                assert (color == joint_ids[joint_id]).all(), f"Bad segmentation color for joint {joint_id}: {color}"
c.communicate({"$type": "terminate"})
```

***

**This is the last document in the "Core Concepts" section. We recommend you next read our guide on [troubleshooting and good coding practices in TDW](../troubleshooting/common_errors.md).**

[Return to the README](../../../README.md)

***

Example Controllers

- [determinism_rng.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/determinism_rng.py) Assert random number generator determinism.
- [determinism_log.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/determinism_log.py) Load a log file and test determinism.

Python API:

- [`Logger`](../../python/add_ons/logger.md)
- [`LogPlayback`](../../python/add_ons/log_playback.md)

Command API:

- [`set_random`](../../api/command_api.md#set_random)

