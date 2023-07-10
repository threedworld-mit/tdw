##### Wheelchair Replicants

# Multi-Agent simulations

*For more information regarding multi-agent simulations, [read this](../multi_agent/overview.md).*

So far, the "simple action loop" of calling `c.communicate([])` until an action ends has been sufficient. This is because all of our controllers have assumed that there is only one agent in the scene, that the agent is a Wheelchair Replicant, and that we don't need to interrupt an action.

Actions and Wheelchair  Replicants are designed for multi-agent simulations in which behavior can be interrupted. The "simple action loop" is useful when showcasing *other* aspects of the Wheelchair Replicant but it's *not necessary*.

## Agents and actions

So far, the Wheelchair Replicant document has focused on the Wheelchair Replicant and has compared it to the Replicant, which works similarly and shares many of the same action classes. TDW has a third agent that uses actions--the [Magnebot](https://github.com/alters-mit/magnebot). The Magnebot works *very* differently that either type of Replicant, so different that it's out of the scope of this document to compare them. However the Magnebot's API is similarly structured around action classes. These action classes can only be used by the Magnebot (and vice versa) but they have the same [code organization](custom_actions.md). 

It's relatively easy to structure a controller that can handle a Magnebot and a Wheelchair Replicant because the high-level logic is similar. Conversely, it's very difficult to structure a controller that can *swap* one agent type for another because they have very different physical rules, shapes, movement patterns, etc.

## The `give.py` controller

We're going to write a very small, simple example controller that shows how a Magnebot and a Wheelchair Replicant can interact. The Magnebot will move to a kitchen counter, pick up an object on top of the counter, go to the Wheelchair Replicant and give the object to the Wheelchair Replicant:

![](images/multiple_agents/give.gif)

### 1. Define the state machines

Like the [custom "clap" action defined in the previous document](custom_actions.md), we're going to use state machine enum values, but this time we'll use them in the context of a controller rather than within the action. The design pattern is essentially the same either way.

Because there are two agents doing two different actions, we need to define two state machines:

```python
from enum import Enum


class MagnebotState(Enum):
    moving_to_cabinet = 0
    reaching_for_target = 1
    grasping_target = 2
    moving_away_from_cabinet = 3
    resetting_arm_after_grasping = 4
    moving_to_replicant = 5
    reaching_for_replicant = 6
    dropping_object = 7
    resetting_arm_after_dropping = 8
    moving_away_from_replicant = 9


class ReplicantState(Enum):
    waiting_for_magnebot = 0
    reaching_for_object = 1
    grasping_object = 2
    moving_away_from_magnebot = 3
```

### 2. Scene setup

The scene setup is pretty typical. We'll run our trial in a `run()` function. Within that, we'll add a [`ThirdPersonCamera`](../core_concepts/avatars.md), [`ImageCapture`](../core_concepts/images.md), and [`ObjectManager`](../core_concepts/objects.md) to the scene. The `ObjectManager` is a little unusual; we will use it to easily get the positions of the kitchen cabinet and the target object.

After that, we need to add the scene, the objects, the Wheelchair Replicant, and the Magnebot. We also need to define two variables that are set to each state machine: `magnebot_state` and `replicant_state`.

Once the scene is loaded, the Magnebot begins by moving towards the cabinet.

```python
from enum import Enum
from tdw.controller import Controller
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from magnebot import Magnebot


class MagnebotState(Enum):
    moving_to_cabinet = 0
    reaching_for_target = 1
    grasping_target = 2
    resetting_arm_after_grasping = 3
    moving_to_replicant = 4
    reaching_for_replicant = 5
    dropping_object = 6
    resetting_arm_after_dropping = 7
    moving_away_from_replicant = 8


class ReplicantState(Enum):
    waiting_for_magnebot = 0
    reaching_for_object = 1
    grasping_object = 2
    moving_away_from_magnebot = 3


class Give(Controller):
    """
    A Magnebot picks up an object and gives it to a WheelchairReplicant.
    """

    def run(self) -> None:
        # Set the IDs.
        cabinet_id: int = Controller.get_unique_id()
        target_id: int = Controller.get_unique_id()
        replicant_id: int = 0
        magnebot_id: int = 1
        # Clear the add-ons.
        self.add_ons.clear()
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(position={"x": 0, "y": 9, "z": 0},
                                   avatar_id="a",
                                   look_at={"x": 0, "y": 0, "z": 0})
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_give")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        # Add a Replicant.
        replicant: WheelchairReplicant = WheelchairReplicant(replicant_id=replicant_id,
                                                             position={"x": 0, "y": 0, "z": -2})
        replicant_state: ReplicantState = ReplicantState.waiting_for_magnebot
        # Add a Magnebot.
        magnebot: Magnebot = Magnebot(robot_id=magnebot_id,
                                      position={"x": -0.5, "y": 0, "z": 1.2},
                                      rotation={"x": 0, "y": 180, "z": 0})
        magnebot.collision_detection.objects = False
        magnebot_state: MagnebotState = MagnebotState.moving_to_cabinet
        # Add an object manager.
        object_manager = ObjectManager(transforms=True, bounds=True, rigidbodies=False)
        self.add_ons.extend([replicant, magnebot, camera, capture, object_manager])
        # Create the scene.
        commands = [Controller.get_add_scene(scene_name="mm_kitchen_2b"),
                    {"$type": "set_floorplan_roof",
                     "show": False}]
        commands.extend(Controller.get_add_physics_object(model_name="cabinet_24_door_drawer_wood_beach_honey",
                                                          object_id=cabinet_id,
                                                          position={"x": 1.94, "y": 0, "z": 2},
                                                          rotation={"x": 0, "y": 90, "z": 0},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                          object_id=target_id,
                                                          position={"x": 1.746, "y": 0.9167836, "z": 1.843}))
        self.communicate(commands)
        # Start moving the Magnebot to the cabinet.
        magnebot.move_to(target=cabinet_id, arrived_at=1)
```

### 3. Main loop

Now we need to define a "main loop", a concept used frequently in game development. This defines a loop controller by a `done` boolean. Within that loop, we'll do the following:

- If the Magnebot finished its action, check `magnebot_state` and decide what to do next. For example, if the Magnebot finished moving to the cabinet, it should start reaching for the target object:

```
        done = False
        while not done:
            # The Magnebot finished an action.
            if magnebot.action.status != MagnebotActionStatus.ongoing:
                # The Magnebot finished moving to the cabinet. Reach for the target object.
                if magnebot_state == MagnebotState.moving_to_cabinet:
                    magnebot_state = MagnebotState.reaching_for_target
                    target_position = object_manager.bounds[target_id].center
                    magnebot.reach_for(target=target_position, arm=MagnebotArm.right)
```

- In *some* cases, we need to check if the Wheelchair Replicant finished its action and decide what to do next. This works similarly to the code snippet above.

- However, for most of this scenario, we want the Wheelchair Replicant to remain motionless and wait for the Magnebot. Therefore, at one section of the code we need to evaluate if the Magenbot's action ended to determine whether the Wheelchair Replicant's state and action should change too. This occurs when the Magnebot will start reaching towards the Wheelchair Replicant; the Wheelchair Replicant should now also reach for the Magnebot.

``` 
                # The Magnebot finished moving to the Replicant. Reach for a position between the two agents.
                elif magnebot_state == MagnebotState.moving_to_replicant:
                    # Get a midpoint.
                    midpoint = (magnebot.dynamic.transform.position + replicant.dynamic.transform.position) / 2
                    midpoint[1] = 0.9
                    # The Magnebot reaches for the midpoint.
                    magnebot.reach_for(target=midpoint, arm=MagnebotArm.right)
                    magnebot_state = MagnebotState.reaching_for_replicant
                    # The Replicant reaches for the midpoint.
                    replicant.reach_for(target=midpoint, arm=ReplicantArm.right)
                    # Set the Replicant's state.
                    replicant_state = ReplicantState.reaching_for_object
```

### 4. Give the object to the Replicant

This is the most complicated part of this controller.

**A Wheelchair Replicant cannot hold an object that any other agent is holding, and vice-versa.** Doing so can result in very strange behavior, or even crash the build.

In order for the Magnebot to give an object to a Wheelchair Replicant, we must do the following:

1. The Magnebot drops the object but doesn't wait for it to fall: `magnebot.drop(target=target_id, arm=MagnebotArm.right, wait_for_object=False)`
2. One `communicate()` call later, the Wheelchair Replicant grasps the object:

```
                # The Replicant finished reaching for the object. Try to grasp the object.
                if replicant_state == ReplicantState.reaching_for_object:
                    # The object can be grasped.
                    if target_id not in magnebot.dynamic.held[MagnebotArm.right]:
                        replicant_state = ReplicantState.grasping_object
                        replicant.grasp(target=target_id, arm=ReplicantArm.right)
```

### 5. Finish writing the agent states

This is the final version of the controller:

```python
from enum import Enum
from tdw.controller import Controller
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.replicant.action_status import ActionStatus as ReplicantActionStatus
from tdw.replicant.arm import Arm as ReplicantArm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from magnebot import Magnebot
from magnebot import ActionStatus as MagnebotActionStatus
from magnebot import Arm as MagnebotArm


class MagnebotState(Enum):
    moving_to_cabinet = 0
    reaching_for_target = 1
    grasping_target = 2
    resetting_arm_after_grasping = 3
    moving_to_replicant = 4
    reaching_for_replicant = 5
    dropping_object = 6
    resetting_arm_after_dropping = 7
    moving_away_from_replicant = 8


class ReplicantState(Enum):
    waiting_for_magnebot = 0
    reaching_for_object = 1
    grasping_object = 2
    moving_away_from_magnebot = 3


class Give(Controller):
    """
    A Magnebot picks up an object and gives it to a WheelchairReplicant.
    """

    def run(self) -> None:
        # Set the IDs.
        cabinet_id: int = Controller.get_unique_id()
        target_id: int = Controller.get_unique_id()
        replicant_id: int = 0
        magnebot_id: int = 1
        # Clear the add-ons.
        self.add_ons.clear()
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(position={"x": 0, "y": 9, "z": 0},
                                   avatar_id="a",
                                   look_at={"x": 0, "y": 0, "z": 0})
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_give")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        # Add a Replicant.
        replicant: WheelchairReplicant = WheelchairReplicant(replicant_id=replicant_id,
                                                             position={"x": 0, "y": 0, "z": -2})
        replicant_state: ReplicantState = ReplicantState.waiting_for_magnebot
        # Add a Magnebot.
        magnebot: Magnebot = Magnebot(robot_id=magnebot_id,
                                      position={"x": -0.5, "y": 0, "z": 1.2},
                                      rotation={"x": 0, "y": 180, "z": 0})
        magnebot.collision_detection.objects = False
        magnebot_state: MagnebotState = MagnebotState.moving_to_cabinet
        # Add an object manager.
        object_manager = ObjectManager(transforms=True, bounds=True, rigidbodies=False)
        self.add_ons.extend([replicant, magnebot, camera, capture, object_manager])
        # Create the scene.
        commands = [Controller.get_add_scene(scene_name="mm_kitchen_2b"),
                    {"$type": "set_floorplan_roof",
                     "show": False}]
        commands.extend(Controller.get_add_physics_object(model_name="cabinet_24_door_drawer_wood_beach_honey",
                                                          object_id=cabinet_id,
                                                          position={"x": 1.94, "y": 0, "z": 2},
                                                          rotation={"x": 0, "y": 90, "z": 0},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                          object_id=target_id,
                                                          position={"x": 1.746, "y": 0.9167836, "z": 1.843}))
        self.communicate(commands)
        # Start moving the Magnebot to the cabinet.
        magnebot.move_to(target=cabinet_id, arrived_at=1)
        done = False
        while not done:
            # The Magnebot finished an action.
            if magnebot.action.status != MagnebotActionStatus.ongoing:
                # The Magnebot finished moving to the cabinet. Reach for the target object.
                if magnebot_state == MagnebotState.moving_to_cabinet:
                    magnebot_state = MagnebotState.reaching_for_target
                    target_position = object_manager.bounds[target_id].center
                    magnebot.reach_for(target=target_position, arm=MagnebotArm.right)
                # The Magnebot finished reaching for the target object. Grasp the object.
                elif magnebot_state == MagnebotState.reaching_for_target:
                    magnebot_state = MagnebotState.grasping_target
                    magnebot.grasp(target=target_id, arm=MagnebotArm.right)
                # The Magnebot finished grasping the target object. Reset the arm.
                elif magnebot_state == MagnebotState.grasping_target:
                    magnebot_state = MagnebotState.resetting_arm_after_grasping
                    magnebot.reset_arm(arm=MagnebotArm.right, set_torso=True)
                # The Magnebot finished resetting its arm. Move to the Replicant.
                elif magnebot_state == MagnebotState.resetting_arm_after_grasping:
                    magnebot_state = MagnebotState.moving_to_replicant
                    magnebot.move_to(target={"x": 0.7, "y": 0, "z": -1.38})
                # The Magnebot finished moving to the Replicant. Reach for a position between the two agents.
                elif magnebot_state == MagnebotState.moving_to_replicant:
                    # Get a midpoint.
                    midpoint = (magnebot.dynamic.transform.position + replicant.dynamic.transform.position) / 2
                    midpoint[1] = 0.9
                    # The Magnebot reaches for the midpoint.
                    magnebot.reach_for(target=midpoint, arm=MagnebotArm.right)
                    magnebot_state = MagnebotState.reaching_for_replicant
                    # The Replicant reaches for the midpoint.
                    replicant.reach_for(target=midpoint, arm=ReplicantArm.right)
                    # Set the Replicant's state.
                    replicant_state = ReplicantState.reaching_for_object
                # The Magnebot and Replicant finished reaching for the position. Drop the object.
                elif magnebot_state == MagnebotState.reaching_for_replicant:
                    if replicant_state == ReplicantState.reaching_for_object and replicant.action.status != ReplicantActionStatus.ongoing:
                        magnebot_state = MagnebotState.dropping_object
                        magnebot.drop(target=target_id, arm=MagnebotArm.right, wait_for_object=False)
                # The Magnebot finished dropping the object. Reset the arm.
                elif magnebot_state == MagnebotState.dropping_object:
                    magnebot_state = MagnebotState.resetting_arm_after_dropping
                    magnebot.reset_arm(arm=MagnebotArm.right)
                # The Magnebot finished resetting the arm. Move away from the Replicant.
                elif magnebot_state == MagnebotState.resetting_arm_after_dropping:
                    magnebot_state = MagnebotState.moving_away_from_replicant
                    magnebot.move_by(distance=-1)
                # We're done!
                else:
                    done = True
            # The Replicant finished an action.
            if replicant_state != ReplicantState.waiting_for_magnebot and replicant.action.status != ReplicantActionStatus.ongoing:
                # The Replicant finished reaching for the object. Try to grasp the object.
                if replicant_state == ReplicantState.reaching_for_object:
                    # The object can be grasped.
                    if target_id not in magnebot.dynamic.held[MagnebotArm.right]:
                        replicant_state = ReplicantState.grasping_object
                        replicant.grasp(target=target_id, arm=ReplicantArm.right)
                # The Replicant finished grasping the object. Turn a little.
                elif replicant_state == ReplicantState.grasping_object:
                    replicant_state = ReplicantState.moving_away_from_magnebot
                    replicant.turn_by(45)
            # Continue the loop.
            self.communicate([])
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Give()
    c.run()
```

## Limitations

**`give.py` is not meant to be an example of an actual use-case.** It has many limitations, all of which are *deliberate*. `give.py` is meant to be a very simplified example of how to write a multi-agent simulation involving a Wheelchair Replicant; the controller doesn't attempt to solve any of the other problems an actual use-case would have to handle.

In `give.py`, the agents use simple state machines but don't actually plan any actions. In an actual use-case, the agents would have to be trained to be responsive to a variety of scenarios.

If either agent's action fails, e.g. if the Magnebot fails to grasp the target object, the controller will hang indefinitely.  In an actual use-case, both agents need to be able to do something to recover from a failed action, such as attempting to move to a better position to reach for a target.

`give.py` doesn't handle navigation or collision detection. The Magnebot moves in a straight line towards each object without checking for obstacles. An actual use-case would have to have navigation planning. 

***

**Next: [Reset](reset.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [give.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/wheelchair_replicant/give.py) A Magnebot picks up an object and gives it to a WheelchairReplicant.

Python API:

- [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md)
- [`Magnebot`](https://github.com/alters-mit/magnebot)