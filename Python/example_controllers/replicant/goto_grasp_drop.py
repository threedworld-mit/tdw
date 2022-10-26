from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class GoToGraspDrop(Controller):
    """
    Walk to an object, grasp it, walk away, and drop it.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Set the replicant and the object IDs here because we need to reference them elsewhere.
        self.replicant = Replicant()
        self.trunk_id = 1
        self.mug_id = 2

    def do_action(self, status: ActionStatus = ActionStatus.success) -> None:
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])
        assert status == self.replicant.action.status, (self.replicant.action.__class__.__name__,
                                                        self.replicant.action.status)

    def run(self) -> None:
        camera = ThirdPersonCamera(position={"x": -1.5, "y": 1.175, "z": 5.25},
                                   look_at={"x": 0.5, "y": 1, "z": 0},
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_go_to_grasp")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant, camera, capture])
        # Create the room.
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="trunck",
                                                          object_id=self.trunk_id,
                                                          position={"x": 0, "y": 0, "z": 3},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="coffeemug",
                                                          object_id=self.mug_id,
                                                          position={"x": 0, "y": 0.9888946, "z": 3}))
        self.communicate(commands)
        self.replicant.move_to(target=self.trunk_id)
        self.do_action(status=ActionStatus.detected_obstacle)
        # Ignore the trunk.
        self.replicant.collision_detection.exclude_objects.append(self.trunk_id)
        self.replicant.reach_for(target=self.mug_id, arm=Arm.right)
        self.do_action()
        self.replicant.grasp(target=self.mug_id, arm=Arm.right, orient_to_floor=False)
        self.do_action()
        self.replicant.move_by(-4)
        self.do_action()
        self.replicant.collision_detection.exclude_objects.clear()
        self.replicant.drop(arm=Arm.right)
        self.do_action()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = GoToGraspDrop()
    c.run()
