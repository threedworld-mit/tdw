from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ReachForOffset(Controller):
    """
    A minimal example of how to reach for a position that is offset by a held object.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = WheelchairReplicant()
        self.camera = ThirdPersonCamera(position={"x": -2.4, "y": 2, "z": 3.2},
                                        look_at=self.replicant.replicant_id,
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_reach_for_offset")
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
        commands.extend(Controller.get_add_physics_object(model_name="side_table_wood",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0.72, "y": 0, "z": 0.1},
                                                          rotation={"x": 0, "y": 90, "z": 0},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                          object_id=object_id,
                                                          position={"x": 0.55, "y": 0.6108887, "z": 0.18}))
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
