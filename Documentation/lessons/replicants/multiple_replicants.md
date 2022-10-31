##### Replicants

# Multi-Replicant simulations

*For more information regarding multi-agent simulations, [read this](../multi_agent/overview.md).*

So far, the "simple action loop" of calling `c.communicate([])` until an action ends has been sufficient. This is because all of our controllers have assumed that there is only one agent in the scene, that the agent is a Replicant, and that we don't need to interrupt an action.

Actions and Replicants are designed for multi-agent simulations in which behavior can be interrupted. The "simple action loop" is useful when showcasing *other* aspects of the Replicant but it's *not necessary*.

## Example A: End when action(s) end

In this example, two replicants will walk forward. We've edited the "simple action loop" to check the states of *both* Replicants' actions. The loop ends when either of the Replicants end. In this case, we know that, because one Replicant needs to walk further than the other, that only the Replicant with the shorter distance will finish its action:

```python
from typing import Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MultiReplicant(Controller):
    def __init__(self, replicants: Dict[int, Dict[str, float]],
                 port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Remember the Replicants. Key = ID. Value = Replicant.
        self.replicants: Dict[int, Replicant] = dict()
        for replicant_id in replicants:
            # Create a Replicant add-on. Set its ID and position.
            replicant = Replicant(replicant_id=replicant_id,
                                  position=replicants[replicant_id])
            # Append the add-on.
            self.add_ons.append(replicant)
            self.replicants[replicant_id] = replicant
        # Add a camera and enable image capture.
        # These aren't field (they don't start with self. ) because we don't need to reference them again.
        camera = ThirdPersonCamera(position={"x": -2.4, "y": 6, "z": 3.2},
                                   look_at={"x": 0, "y": 1, "z": 0},
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_replicant")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
        self.add_ons.extend([camera, capture])
        # Create an empty scene.
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def do_actions(self) -> None:
        # Loop.
        done = False
        while not done:
            for replicant_id in self.replicants:
                # One of the actions ended. Stop.
                if self.replicants[replicant_id].action.status != ActionStatus.ongoing:
                    done = True
            # Continue the loop.
            if not done:
                self.communicate([])
        self.communicate([])


if __name__ == "__main__":
    c = MultiReplicant(replicants={0: {"x": 1.5, "y": 0, "z": -1},
                                   1: {"x": -1.5, "y": 0, "z": -1}})
    c.replicants[0].move_by(distance=2)
    c.replicants[1].move_by(distance=4)
    c.do_actions()
    print(c.replicants[0].action.status)
    print(c.replicants[1].action.status)
    c.communicate({"$type": "terminate"})
```

Result:

![](images/multiple_replicants/move_by_stop.gif)

Output:

```
ActionStatus.success
ActionStatus.ongoing
```

We can easily revise the loop to end when *both* Replicants end their actions:

```python
from typing import Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MultiReplicant(Controller):
    def __init__(self, replicants: Dict[int, Dict[str, float]],
                 port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Remember the Replicants. Key = ID. Value = Replicant.
        self.replicants: Dict[int, Replicant] = dict()
        for replicant_id in replicants:
            # Create a Replicant add-on. Set its ID and position.
            replicant = Replicant(replicant_id=replicant_id,
                                  position=replicants[replicant_id])
            # Append the add-on.
            self.add_ons.append(replicant)
            self.replicants[replicant_id] = replicant
        # Add a camera and enable image capture.
        # These aren't field (they don't start with self. ) because we don't need to reference them again.
        camera = ThirdPersonCamera(position={"x": -2.4, "y": 6, "z": 3.2},
                                   look_at={"x": 0, "y": 1, "z": 0},
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_replicant")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
        self.add_ons.extend([camera, capture])
        # Create an empty scene.
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def do_actions(self) -> None:
        # Loop.
        done = False
        while not done:
            done = True
            for replicant_id in self.replicants:
                # One of the actions is ongoing. We're not done.
                if self.replicants[replicant_id].action.status == ActionStatus.ongoing:
                    done = False
            # Continue the loop.
            if not done:
                self.communicate([])
        self.communicate([])


if __name__ == "__main__":
    c = MultiReplicant(replicants={0: {"x": 1.5, "y": 0, "z": -1},
                                   1: {"x": -1.5, "y": 0, "z": -1}})
    c.replicants[0].move_by(distance=2)
    c.replicants[1].move_by(distance=4)
    c.do_actions()
    print(c.replicants[0].action.status)
    print(c.replicants[1].action.status)
    c.communicate({"$type": "terminate"})
```

Result:

![](images/multiple_replicants/move_by.gif)

Output:

```
ActionStatus.success
ActionStatus.success
```

## Example B: State machines

In this example,  there are two replicants:

1. `replicant_0` will [play a dance animation](animations.md) in a loop. We'll control the behavior of `replicant_0` by simply checking if the animation is done.
2. `replicant_1` will try to walk to the other side of the room. If it gets too close to `replicant_0`, it will back up and try again. We'll control the behavior of `replicant_1` with a state machine, similar to how we handled [custom actions in the previous document](custom_actions.md). Before calling `communicate([])` we'll evaluate the Replicant's state and its action status and decide what it should do next:

```python
from enum import Enum
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class Replicant1State(Enum):
    moving_to = 1
    moving_backward = 2
    turning = 3
    moving_forward = 4


class MultiReplicantStateMachine(Controller):
    """
    Control the actions of multiple Replicants using a state machine.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant_0 = Replicant(replicant_id=0,
                                     position={"x": 0, "y": 0, "z": 0})
        self.replicant_1 = Replicant(replicant_id=1,
                                     position={"x": 0, "y": 0, "z": -2})
        camera = ThirdPersonCamera(position={"x": -4, "y": 3, "z": 3.2},
                                   look_at=self.replicant_1.replicant_id,
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_replicant_state_machine")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
        self.add_ons.extend([self.replicant_0, self.replicant_1, camera, capture])
        # Create an empty scene.
        self.communicate(TDWUtils.create_empty_room(12, 12))
        # Start animating.
        self.replicant_0_animation: str = "dancing_3"
        self.replicant_0.animate(animation=self.replicant_0_animation)
        # Set Replicant 1's target to be 6 meters in front of it.
        self.replicant_1_target = {"x": self.replicant_1.initial_position["x"],
                                   "y": self.replicant_1.initial_position["y"],
                                   "z": self.replicant_1.initial_position["z"] + 6}
        # Start moving.
        self.replicant_1.move_to(target=self.replicant_1_target)
        self.replicant_1_state = Replicant1State.moving_to

    def run(self) -> None:
        done = False
        while not done:
            # The animation ended. Play it again.
            if self.replicant_0.action.status != ActionStatus.ongoing:
                self.replicant_0.animate(animation=self.replicant_0_animation)

            # Handle Replicant 1's state machine.
            # Check if the action succeeded.
            if self.replicant_1.action.status == ActionStatus.success:
                # The Replicant finished moving forward. We're done.
                if self.replicant_1_state == Replicant1State.moving_to:
                    done = True
                # The Replicant finished moving backwards. Start turning.
                elif self.replicant_1_state == Replicant1State.moving_backward:
                    self.replicant_1_state = Replicant1State.turning
                    self.replicant_1.turn_by(35)
                # The Replicant finished turning. Start moving forward.
                elif self.replicant_1_state == Replicant1State.turning:
                    self.replicant_1.move_by(distance=0.75)
                    self.replicant_1_state = Replicant1State.moving_forward
                # The Replicant finished moving forward. Start moving to the target again.
                elif self.replicant_1_state == Replicant1State.moving_forward:
                    self.replicant_1.move_to(target=self.replicant_1_target)
                    self.replicant_1_state = Replicant1State.moving_to
            # The action ended in failure.
            elif self.replicant_1.action.status != ActionStatus.ongoing:
                # Start backing up.
                self.replicant_1_state = Replicant1State.moving_backward
                self.replicant_1.move_by(distance=-0.5)

            # Continue the loop.
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MultiReplicantStateMachine()
    c.run()
```

Result:

![](images/multiple_replicants/state_machine.gif)
