from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MoveGraspDrop(Controller):
    """
    Move to an object, grasp it, move away, and drop it.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Set the replicant and the object IDs here because we need to reference them elsewhere.
        self.replicant = WheelchairReplicant()
        self.table_id = 1
        self.mug_id = 2

    def do_action(self) -> None:
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])

    def run(self) -> None:
        camera = ThirdPersonCamera(position={"x": -3.5, "y": 1.175, "z": 1},
                                   avatar_id="a",
                                   look_at=self.replicant.replicant_id)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_move_grasp_drop")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant, camera, capture])
        # Create the room.
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="side_table_wood",
                                                          object_id=self.table_id,
                                                          position={"x": -1.8, "y": 0, "z": 1.3},
                                                          rotation={"x": 0, "y": 70, "z": 0},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                          object_id=self.mug_id,
                                                          rotation={"x": 0, "y": 180, "z": 0},
                                                          position={"x": -1.6, "y": 0.6108887, "z": 1.358}))
        self.communicate(commands)
        self.replicant.collision_detection.avoid = False
        self.replicant.collision_detection.objects = False
        self.replicant.move_to(target={"x": -1.05, "y": 0, "z": 1.485}, arrived_at=0.1)
        self.do_action()
        self.replicant.reach_for(target=self.mug_id, arm=Arm.left)
        self.do_action()
        self.replicant.grasp(target=self.mug_id, arm=Arm.left, offset=0.2, relative_to_hand=False, angle=0)
        self.do_action()
        self.replicant.move_by(-2, reset_arms=False)
        self.do_action()
        self.replicant.drop(arm=Arm.left)
        self.do_action()
        self.replicant.move_by(-2)
        self.do_action()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MoveGraspDrop()
    c.run()
