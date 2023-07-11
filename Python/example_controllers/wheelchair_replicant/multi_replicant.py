from typing import Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MultiReplicant(Controller):
    """
    A minimal multi-Replicant simulation.
    """

    def __init__(self, replicants: Dict[int, Dict[str, float]],
                 port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Remember the Replicants. Key = ID. Value = Replicant.
        self.replicants: Dict[int, WheelchairReplicant] = dict()
        for replicant_id in replicants:
            # Create a Replicant add-on. Set its ID and position.
            replicant = WheelchairReplicant(replicant_id=replicant_id,
                                            position=replicants[replicant_id])
            # Append the add-on.
            self.add_ons.append(replicant)
            self.replicants[replicant_id] = replicant
        # Add a camera and enable image capture.
        # These aren't field (they don't start with self. ) because we don't need to reference them again.
        camera = ThirdPersonCamera(position={"x": -2.4, "y": 6, "z": 3.2},
                                   look_at={"x": 0, "y": 1, "z": 0},
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_wheelchair_replicant")
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
