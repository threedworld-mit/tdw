##### Replicants

# Custom actions

[Replicant actions](actions.md) are designed to be easily subclassed. This document will cover two basic strategies for creating custom actions, as well as how to improve [the previous NavMesh example.](navigation.md)

## 1. How to create a minimal `DoNothing` action

Every action needs to be a subclass of [`Action`](../../python/replicant/actions/action.md) or a subclass of one of its subclasses. Every action needs to define `get_initialization_commands(resp, static, dynamic, image_frequency)` and `get_ongoing_commands(resp, static, dynamic)`.

This is a minimal action:

```python
from typing import List
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class DoNothing(Action):
    """
    A minimal custom action.
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the standard initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []
```

- In both functions, `resp` is the latest response from the build. Many actions need this to parse arbitrary output data. `static` is the Replicant's [`ReplicantStatic`](../../python/replicant/replicant_static.md) and `dynamic` is the Replicant's [`ReplicantDynamic`](../../python/replicant/replicant_dynamic.md); these will be handled within the `Replicant` add-on.
- *Always* add `commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)`. This will set up the camera and image capture correctly.
- In `self.ongoing_commands(resp, static, dynamic)`, we want the command to end immediately in success, so we added `self.status = ActionStatus.success`.

You can optionally add `get_end_commands(resp, static, dynamic, image_frequency)`. *This is not necessary.* You only need to add it if you need the action to send extra commands when it ends. This function always gets called when an action ends, regardless of whether it succeeds:

```python
from typing import List
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class DoNothing(Action):
    """
    A minimal custom action.
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the standard initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []
    
    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
```

To add this action do a controller, simply manually assign `replicant.action = DoNothing()`:

```python
from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.add_ons.replicant import Replicant
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class DoNothing(Action):
    """
    A minimal custom action.
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the standard initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []
    
    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)


if __name__ == "__main__":
    c = Controller()
    replicant = Replicant()
    c.add_ons.append(replicant)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    replicant.action = DoNothing()
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])
    print(replicant.action.status)
    c.communicate({"$type": "terminate"})
```

Output:

```
ActionStatus.success
```

You can wrap the new `DoNothing` action in a Replicant function such as `replicant.do_nothing()`. This is totally optional, though. If you wish to do this, create a custom subclass of Replicant and add your function:

```python
from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.add_ons.replicant import Replicant
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class DoNothing(Action):
    """
    A minimal custom action.
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the standard initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
    

class MyReplicant(Replicant):
    def do_nothing(self) -> None:
        self.action = DoNothing()


if __name__ == "__main__":
    c = Controller()
    replicant = MyReplicant()
    c.add_ons.append(replicant)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    replicant.do_nothing()
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])
    print(replicant.action.status)
    c.communicate({"$type": "terminate"})
```

## 2. How to create an action using a state machine and create a `Clap` action

Now we're going to define a much more complicated action: `Clap`, which tells the Replicant to clap its hands.

### 2.1 Create the state machine

We're going to use a *state machine* to handle the motion. A state machine is a basic concept in algorithms that just means that the action has been divided into discrete *states*. In this case, there are three states:

1. The Replicant raises its hands.
2. The Replicant brings its hands together.
3. The Replicant pulls its hands apart.

When state 1 ends, state 2 begins. When state 2 ends, state 3 begins. When state 3 ends, the action ends.

To start, we'll define our state machine as a subclass of `Enum`:

```python
from enum import Enum

class ClapState(Enum):
    raising_hands = 1
    coming_together = 2
    pulling_apart = 4
```

### 2.2 Create the `Clap` constructor

Now we're going to start to write our `Clap` action. Instead of being a subclass of `Action`, this will be a subclass of [`ArmMotion`](../../python/replicant/actions/arm_motion.md), the abstract class used by [`ReachFor`](../../python/replicant/actions/reach_for.md) and [`ResetArm`](../../python/replicant/actions/reset_arm.md). We want to subclass `ArmMotion` because it automatically handles [collision detection](collision_detection.md) for us while the arms are moving:

```python
from enum import Enum
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm


class ClapState(Enum):
    raising_hands = 1
    coming_together = 2
    pulling_apart = 4


class Clap(ArmMotion):
    """
    Clap your hands.
    """
    
    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection):
        super().__init__(arms=[Arm.left, Arm.right], dynamic=dynamic, collision_detection=collision_detection,
                         duration=0.1, previous=None)
        self.clap_state: ClapState = ClapState.raising_hands
```

- We need to call `super().__init__(...)` because that will call the constructor for `ArmMotion` and set up the rest of the action correctly. We've set `arms` to both arms because you need both hands to clap, and `duration` to a fast speed.
- `self.clap_state` will manage the state machine of this action. When the action begins, the state is `raising_hands`.

### 2.3 Define helper functions

We're going to use a few helper functions that will be used throughout the rest of the function.

First, we need a function that defines the position where the clap will occur. This should be at chest-height, in front of the Replicant:

```python
from enum import Enum
import numpy as np
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm


class ClapState(Enum):
    raising_hands = 1
    coming_together = 2
    pulling_apart = 4


class Clap(ArmMotion):
    """
    Clap your hands.
    """

    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection):
        super().__init__(arms=[Arm.left, Arm.right], dynamic=dynamic, collision_detection=collision_detection,
                         duration=0.1, previous=None)
        self.clap_state: ClapState = ClapState.raising_hands

    @staticmethod
    def get_clap_position(dynamic: ReplicantDynamic) -> np.ndarray:
        # Get a position in front of the Replicant.
        position = dynamic.transform.position.copy()
        # Move the position in front of the Replicant.
        position += dynamic.transform.forward * 0.4
        # Set the height of the position.
        position[1] = 1.5
        return position
```

Next, we need a function for the initial positions of the hands. We'll get the "clap position" and then rotate it -90 degrees and 90 degrees for the left and right hands. Then, we'll return two [`replicant_reach_for_position`](../../api/command_api.md#replicant_reach_for_position) commands:

```python
from enum import Enum
import numpy as np
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm


class ClapState(Enum):
    raising_hands = 1
    coming_together = 2
    pulling_apart = 4


class Clap(ArmMotion):
    """
    Clap your hands.
    """

    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection):
        super().__init__(arms=[Arm.left, Arm.right], dynamic=dynamic, collision_detection=collision_detection,
                         duration=0.1, previous=None)
        self.clap_state: ClapState = ClapState.raising_hands

    @staticmethod
    def get_clap_position(dynamic: ReplicantDynamic) -> np.ndarray:
        # Get a position in front of the Replicant.
        position = dynamic.transform.position.copy()
        # Move the position in front of the Replicant.
        position += dynamic.transform.forward * 0.4
        # Set the height of the position.
        position[1] = 1.5
        return position
    
    def get_initial_position_commands(self, static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Get the position.
        position = Clap.get_clap_position(dynamic=dynamic)
        origin = dynamic.transform.position.copy()
        origin[1] = position[1]
        forward = dynamic.transform.forward * 0.4
        # Rotate the position to the side.
        left = TDWUtils.rotate_position_around(position=position,
                                               origin=origin,
                                               angle=-90)
        # Move the position forward.
        left += forward
        # Rotate the position to the side.
        right = TDWUtils.rotate_position_around(position=position,
                                                origin=origin,
                                                angle=90)
        # Move the position forward.
        right += forward
        commands = []
        # Reach for the initial positions.
        for arm, position in zip(self.arms, [left, right]):
            commands.append({"$type": "replicant_reach_for_position",
                             "id": static.replicant_id,
                             "position": TDWUtils.array_to_vector3(position),
                             "duration": self.duration,
                             "arm": arm.name})
        return commands
```

### 2.4 Define `get_initialization_commands()`

As with all actions, we need to define `get_initialization_commands(resp, static, dynamic, image_frequency)`. In this case, we'll get the standard initialization commands with `super()` and then extend that list with `get_initial_position_commands(static, dynamic)`:

```python
from typing import List
from enum import Enum
import numpy as np
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency


class ClapState(Enum):
    raising_hands = 1
    coming_together = 2
    pulling_apart = 4


class Clap(ArmMotion):
    """
    Clap your hands.
    """

    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection):
        super().__init__(arms=[Arm.left, Arm.right], dynamic=dynamic, collision_detection=collision_detection,
                         duration=0.1, previous=None)
        self.clap_state: ClapState = ClapState.raising_hands
        
    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the standard initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Get the initial position of each hand.
        commands.extend(self.get_initial_position_commands(static=static, dynamic=dynamic))
        return commands

    @staticmethod
    def get_clap_position(dynamic: ReplicantDynamic) -> np.ndarray:
        # Get a position in front of the Replicant.
        position = dynamic.transform.position.copy()
        # Move the position in front of the Replicant.
        position += dynamic.transform.forward * 0.4
        # Set the height of the position.
        position[1] = 1.5
        return position

    def get_initial_position_commands(self, static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Get the position.
        position = Clap.get_clap_position(dynamic=dynamic)
        origin = dynamic.transform.position.copy()
        origin[1] = position[1]
        forward = dynamic.transform.forward * 0.4
        # Rotate the position to the side.
        left = TDWUtils.rotate_position_around(position=position,
                                               origin=origin,
                                               angle=-90)
        # Move the position forward.
        left += forward
        # Rotate the position to the side.
        right = TDWUtils.rotate_position_around(position=position,
                                                origin=origin,
                                                angle=90)
        # Move the position forward.
        right += forward
        commands = []
        # Reach for the initial positions.
        for arm, position in zip(self.arms, [left, right]):
            commands.append({"$type": "replicant_reach_for_position",
                             "id": static.replicant_id,
                             "position": TDWUtils.array_to_vector3(position),
                             "duration": self.duration,
                             "arm": arm.name})
        return commands
```

### 2.5 Define `get_ongoing_commands()`

This is where most of any action's logic is handled. This action gets call on every `communicate()` call. We'll use it to evaluate the current state of the Replicant and update the state if needed.

First, we'll call `super()`, which, because this is a subclass of `ArmMotion`, will check for collisions:

```
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Continue the action, checking for collisions.
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
```

If `self.status != ActionStatus.ongoing`, that doesn't mean that action has *actually* ended; it just means that the current *motion* has ended. Every time the Replicant finishes reaching for a target, the build will signal that the motion is complete. We're going to use that information to check whether we need to start the next *clap state*:

```
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Continue the action, checking for collisions.
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # The motion ended. Decide if we need to do more motions.
        # It's ok in this case if the motion ends in failed_to_reach because we don't need it to be precise.
        if self.status == ActionStatus.success or self.status == ActionStatus.failed_to_reach:
```

The initial clap state is `raising_hands`. If the *motion* ended and the *state* is `raising_hands`, then we need to set our *status* to `ongoing` and the *state* to `coming_together`. We also need to reach for a new target position:

```
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Continue the action, checking for collisions.
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # The motion ended. Decide if we need to do more motions.
        # It's ok in this case if the motion ends in failed_to_reach because we don't need it to be precise.
        if self.status == ActionStatus.success or self.status == ActionStatus.failed_to_reach:
            # We're done raising the hands. Bring the hands together.
            if self.clap_state == ClapState.raising_hands:
                # The action is ongoing.
                self.status = ActionStatus.ongoing
                # The state is coming together.
                self.clap_state = ClapState.coming_together
                # Get a position in front of the Replicant.
                position = self.get_clap_position(dynamic=dynamic)
                # Tell both hands to reach for the target position.
                commands = []
                for arm in self.arms:
                    commands.append({"$type": "replicant_reach_for_position",
                                     "id": static.replicant_id,
                                     "position": TDWUtils.array_to_vector3(position),
                                     "duration": self.duration,
                                     "arm": arm.name})
```

If the *motion* ends and the *state* is `coming_together`, then it's time to pull the hands apart:

```
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Continue the action, checking for collisions.
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # The motion ended. Decide if we need to do more motions.
        # It's ok in this case if the motion ends in failed_to_reach because we don't need it to be precise.
        if self.status == ActionStatus.success or self.status == ActionStatus.failed_to_reach:
            # We're done raising the hands. Bring the hands together.
            if self.clap_state == ClapState.raising_hands:
                # The action is ongoing.
                self.status = ActionStatus.ongoing
                # The state is coming together.
                self.clap_state = ClapState.coming_together
                # Get a position in front of the Replicant.
                position = self.get_clap_position(dynamic=dynamic)
                # Tell both hands to reach for the target position.
                commands = []
                for arm in self.arms:
                    commands.append({"$type": "replicant_reach_for_position",
                                     "id": static.replicant_id,
                                     "position": TDWUtils.array_to_vector3(position),
                                     "duration": self.duration,
                                     "arm": arm.name})
            # We're done moving the hands together. Bring the hands apart again.
            elif self.clap_state == ClapState.coming_together:
                # The action is ongoing.
                self.status = ActionStatus.ongoing
                # The state is pulling apart.
                self.clap_state = ClapState.pulling_apart
                # Reach for the initial positions.
                commands.extend(self.get_initial_position_commands(static=static, dynamic=dynamic))
```

If the *motion* ends and the *state* is `pulling_apart`, then the action is done.

### 2.6 Use `Clap` in a controller

We'll assign and run `Clap` the same way we assigned and ran `DoNothing`:

```python
from typing import List
from enum import Enum
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.add_ons.replicant import Replicant
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency


class ClapState(Enum):
    raising_hands = 1
    coming_together = 2
    pulling_apart = 4


class Clap(ArmMotion):
    """
    Clap your hands.
    """

    def __init__(self, dynamic: ReplicantDynamic, collision_detection: CollisionDetection):
        super().__init__(arms=[Arm.left, Arm.right], dynamic=dynamic, collision_detection=collision_detection,
                         duration=0.1, previous=None)
        self.clap_state: ClapState = ClapState.raising_hands

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the standard initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Get the initial position of each hand.
        commands.extend(self.get_initial_position_commands(static=static, dynamic=dynamic))
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Continue the action, checking for collisions.
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # The motion ended. Decide if we need to do more motions.
        # It's ok in this case if the motion ends in failed_to_reach because we don't need it to be precise.
        if self.status == ActionStatus.success or self.status == ActionStatus.failed_to_reach:
            # We're done raising the hands. Bring the hands together.
            if self.clap_state == ClapState.raising_hands:
                # The action is ongoing.
                self.status = ActionStatus.ongoing
                # The state is coming together.
                self.clap_state = ClapState.coming_together
                # Get a position in front of the Replicant.
                position = self.get_clap_position(dynamic=dynamic)
                # Tell both hands to reach for the target position.
                commands = []
                for arm in self.arms:
                    commands.append({"$type": "replicant_reach_for_position",
                                     "id": static.replicant_id,
                                     "position": TDWUtils.array_to_vector3(position),
                                     "duration": self.duration,
                                     "arm": arm.name})
            # We're done moving the hands together. Bring the hands apart again.
            elif self.clap_state == ClapState.coming_together:
                # The action is ongoing.
                self.status = ActionStatus.ongoing
                # The state is pulling apart.
                self.clap_state = ClapState.pulling_apart
                # Reach for the initial positions.
                commands.extend(self.get_initial_position_commands(static=static, dynamic=dynamic))
            # If the motion is successful and the state is `pulling_apart`, then we're done.
            elif self.clap_state == ClapState.pulling_apart:
                self.status = ActionStatus.success
        return commands

    @staticmethod
    def get_clap_position(dynamic: ReplicantDynamic) -> np.ndarray:
        # Get a position in front of the Replicant.
        position = dynamic.transform.position.copy()
        # Move the position in front of the Replicant.
        position += dynamic.transform.forward * 0.4
        # Set the height of the position.
        position[1] = 1.5
        return position

    def get_initial_position_commands(self, static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Get the position.
        position = Clap.get_clap_position(dynamic=dynamic)
        origin = dynamic.transform.position.copy()
        origin[1] = position[1]
        forward = dynamic.transform.forward * 0.4
        # Rotate the position to the side.
        left = TDWUtils.rotate_position_around(position=position,
                                               origin=origin,
                                               angle=-90)
        # Move the position forward.
        left += forward
        # Rotate the position to the side.
        right = TDWUtils.rotate_position_around(position=position,
                                                origin=origin,
                                                angle=90)
        # Move the position forward.
        right += forward
        commands = []
        # Reach for the initial positions.
        for arm, position in zip(self.arms, [left, right]):
            commands.append({"$type": "replicant_reach_for_position",
                             "id": static.replicant_id,
                             "position": TDWUtils.array_to_vector3(position),
                             "duration": self.duration,
                             "arm": arm.name})
        return commands


if __name__ == "__main__":
    c = Controller()
    replicant = Replicant()
    camera = ThirdPersonCamera(position={"x": 2, "y": 3, "z": 2.53},
                               look_at=replicant.replicant_id,
                               avatar_id="a")
    path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_clap")
    print(f"Images will be saved to: {path}")
    capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
    c.add_ons.extend([replicant, camera, capture])
    c.communicate(TDWUtils.create_empty_room(12, 12))
    replicant.action = Clap(dynamic=replicant.dynamic, collision_detection=replicant.collision_detection)
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
    c.communicate([])
    print(replicant.action.status)
    c.communicate({"$type": "terminate"})
```

Result:

![](images/clap.gif)

## 4. How to perform actions within actions and create a `Navigate` action

It's often useful to perform existing actions within actions. [`MoveTo`](../../python/replicant/actions/move_to.md), for example, first does a [`TurnTo`](../../python/replicant/actions/turn_to.md)  action followed by a [`MoveBy`](../../python/replicant/actions/move_by.md) action (and it uses a state machine to decide which action to perform). For the sake of clarity, we'll differentiate between the "parent action" and "child action" but these are informal terms. The parent action is the one being assigned to `replicant.action` and the child action is being referenced within the parent action. There can be multiple child actions in a list but only one should be referenced per `communicate()` call.

Referencing a child action within a parent action is simple:

- Within the parent action's `get_initialization_commands()`, function, append the commands from `child.get_initialization_commands()`. 
- Within the parent action's `get_ongoing_commands()`, function, append the commands from `child.get_ongoing_commands()`.  If needed, reference `child.status` as well.
- If needed, within the parent action's `get_end_commands()`, function, append the commands from `child.get_end_commands()`.

In this example, we'll define a `Navigate` action. This will be similar to [the previous NavMesh example](navigation.md) but with one big difference: by handling the motion in an action, we can detach it from the standard `do_action()` loop, meaning that the action can be interrupted and that it can be used in a [multi-agent simulation](multiple_replicants.md).

Once again, we'll define a state machine:

