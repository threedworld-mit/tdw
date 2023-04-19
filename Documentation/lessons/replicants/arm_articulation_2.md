##### Replicants

# Arm articulation, pt. 2

Replicant arm articulation is a complex topic. [The previous document](arm_articulation_1.md) covered basic arm articulation actions. This document covers more advanced examples that use some additional optional parameters.

## Make one hand follow the other

During a `reach_for(target, arm)` action, If the `arm` parameter is a single value (e.g. `Arm.left`, not `[Arm.left, Arm.right]`), you can set the optional parameter `offhand_follows=True`. This will make the offhand (the opposite of whatever `arm` is set to) follow the primary hand:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

c = Controller()
replicant = Replicant()
camera = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": 2.5},
                           look_at=replicant.replicant_id,
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_reach_for_follow")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
c.add_ons.extend([replicant, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
# Reach for a target with the right hand.
replicant.reach_for(target={"x": 0.6, "y": 1.5, "z": 0.3}, arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
# Reach for a target with the left hand.
replicant.reach_for(target={"x": -0.4, "y": 1, "z": 0.1}, arm=Arm.left)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
# Reach for a target with the right hand and have the left hand follow.
replicant.reach_for(target={"x": 0.8, "y": 0.8, "z": 0.3}, arm=Arm.right, offhand_follows=True)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

![](images/arm_articulation/reach_for_follow.gif)

## Offset a target position by a held object

In many scenarios, you might want the target position to change if the Replicant is holding an object. For example, if you want the Replicant to place a plate on a table, then you will want the Replicant to move the *plate* to the target position rather than the *hand*. You can achieve this by setting two optional parameters in the `reach_for()` action: `from_held` and `held_point`.

`from_held` is a boolean that by default is False. If True, the Replicant will offset the action's target position by a point on the held object. If the hand isn't holding an object, this is ignored.

`held_point` is a string describing a bounds position such as `"bottom"`, `"top"`, etc. that will be used to calculate the offset from the hand. It defaults to `"bottom"` and is only used if `from_held=True` (and if the Replicant is actually holding an object). In the above scenario, where we want the Replicant to place a plate on a table,  we probably want to set `held_point="bottom"`. 

In this example, the Replicant will grasp an object and then reach for the same positioning but applying different offsets per trial. For more information regarding the `grasp()` action, read [the next document in this lesson](grasp_drop.md).

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ReachForOffset(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = Replicant()
        self.camera = ThirdPersonCamera(position={"x": -2.4, "y": 2, "z": 3.2},
                                        look_at=self.replicant.replicant_id,
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_reach_for_offset")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=[self.camera.avatar_id], path=path)
        self.add_ons.extend([self.replicant, self.camera, self.capture])

    def do_action(self):
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])

    def trial(self, from_held: bool, held_point: str):
        # Reset the add-ons.
        self.replicant.reset()
        self.camera.initialized = False
        self.capture.initialized = False
        # Load the scene.
        object_id = Controller.get_unique_id()
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="basket_18inx18inx12iin_wicker",
                                                          object_id=object_id,
                                                          position={"x": 0.2, "y": 0, "z": 0.7},
                                                          rotation={"x": 0, "y": 40, "z": 0}))
        self.communicate(commands)
        self.replicant.reach_for(target=object_id, arm=Arm.right)
        self.do_action()
        self.replicant.grasp(target=object_id, arm=Arm.right, relative_to_hand=False, axis="pitch", angle=0)
        self.do_action()
        self.replicant.reach_for(target={"x": 0.1, "y": 1.1, "z": 0.6}, arm=Arm.right, absolute=False,
                                 from_held=from_held, held_point=held_point)
        self.do_action()


if __name__ == "__main__":
    c = ReachForOffset()
    c.trial(from_held=False, held_point="")
    c.trial(from_held=True, held_point="bottom")
    c.trial(from_held=True, held_point="top")
    c.communicate({"$type": "terminate"})
```

Result:

![](images/arm_articulation/reach_for_offset.gif)

## Divide a `reach_for(target, arm)` action using an IK Plan

In many cases, it's not desirable for the Replicant to simply reach towards a target position. For example, if the Replicant is [grasping an object](grasp_drop.md) that is only the floor and wants to put the object on a kitchen counter, it shouldn't move its hand directly towards the surface of the counter because the hand will collide with a cabinet door along the way.

The best way to solve this is to subdivide a single motion into multiple motions. In TDW, this subdivided motion is handled using an IkPlan. To set the plan for the action, set the optional `plan` parameter to a [`IkPlanType`](../../python/replicant/ik_plans/ik_plan_type.md) value. For example: `plan=IkPlanType.vertical_horizontal`.

**There is no bounded solution for when to use IkPlans.** There is no way to determine using a simple algorithm which plan, if any, is correct for any given situation, because "correctness" is impossible to define. For example, it is often possible for the Replicant to reach for a position without a plan *and* with a plan, meaning that both options could be considered equally "correct". It is up to the user or the training system to decide which plan, if any, to use for a given `reach_for()` action.

In the example, there are two trials. In both trials, the Replicant reaches for a mug and [grasps it](grasp_drop.md) and tries to drop the mug on the trunk. If the hand or arm collides with the trunk, the trial ends in failure. In the first trial, the Replicant doesn't set the `plan` parameter. In the second trial, the Replicant uses `IkPlanType.vertical_horizontal`, thereby splitting the motion into vertical and horizontal components.

```python
from typing import Optional
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.replicant.ik_plans.ik_plan_type import IkPlanType
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ReachForWithPlan(Controller):
    """
    An example of the difference between a simple `reach_for()` motion and a `reach_for()` motion with a plan.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = Replicant()
        self.camera = ThirdPersonCamera(position={"x": -3.5, "y": 1.175, "z": 3},
                                        avatar_id="a",
                                        look_at=self.replicant.replicant_id)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_reach_for_with_plan")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant, self.camera, self.capture])

    def do_action(self) -> None:
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])

    def trial(self, plan: Optional[IkPlanType]):
        self.replicant.reset()
        self.camera.initialized = False
        self.capture.initialized = False
        table_id = 1
        mug_id = 2
        table_z = 3
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                          object_id=table_id,
                                                          position={"x": 0, "y": 0, "z": table_z},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                          object_id=mug_id,
                                                          position={"x": 0, "y": 0, "z": table_z - 0.4}))
        self.communicate(commands)
        # Move to the trunk.
        self.replicant.move_to(target=mug_id)
        self.do_action()
        # Reach for an grasp the mug.
        self.replicant.reach_for(target=mug_id, arm=Arm.right)
        self.do_action()
        self.replicant.grasp(target=mug_id, arm=Arm.right)
        self.do_action()
        # Reach above the trunk. Use the `plan`, which may be None.
        self.replicant.reach_for(target={"x": 0, "y": 1.1, "z": table_z},
                                 arm=Arm.right,
                                 plan=plan,
                                 from_held=True)
        self.do_action()
        # If the reach_for() action failed, stop here.
        if self.replicant.action.status != ActionStatus.success:
            return self.replicant.action.status
        # Drop the object on the trunk.
        self.replicant.drop(arm=Arm.right, max_num_frames=200)
        self.do_action()
        return self.replicant.action.status


if __name__ == "__main__":
    c = ReachForWithPlan()
    for p in [None, IkPlanType.vertical_horizontal]:
        s = c.trial(plan=p)
        print(s)
    c.communicate({"$type": "terminate"})
```

Result:

![](images/arm_articulation/reach_for_with_plan.gif)

Output:

```
ActionStatus.collision
ActionStatus.success
```

***

**Next: [Grasp and drop objects](grasp_drop.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [reach_for_follow.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/replicant/reach_for_follow.py) Reach for a target position and have the offhand follow the main hand.
- [reach_for_offset.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/replicant/reach_for_offset.py) A minimal example of how to reach for a position that is offset by a held object.
- [reach_for_with_plan.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/replicant/reach_for_with_plan.py) An example of the difference between a `reach_for()` action with and without a plan.

Python API:

- [`Replicant`](../../python/add_ons/replicant.md)
- [`Arm`](../../python/replicant/arm.md)
- [`ReachFor`](../../python/replicant/actions/reach_for.md)
- [`ReachForWithPlan`](../../python/replicant/actions/reach_for_with_plan.md)
- [`IkPlanType`](../../python/replicant/ik_plans/ik_plan_type.md)
- [`IkPlan`](../../python/replicant/ik_plans/ik_plan.md)
- [`VerticalHorizontal`](../../python/replicant/ik_plans/vertical_horizontal.md)
