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
                         duration=0.025, previous=None)
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
    camera = ThirdPersonCamera(position={"x": 0, "y": 1.5, "z": 2.5},
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
