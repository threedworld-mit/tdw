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
