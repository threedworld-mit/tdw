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
    An example of the difference between a `reach_for()` action with and without a plan.
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
        # Reach for and grasp the mug.
        self.replicant.reach_for(target=mug_id, arm=Arm.right)
        self.do_action()
        self.replicant.grasp(target=mug_id, arm=Arm.right, angle=0, axis="pitch", relative_to_hand=False)
        self.do_action()
        # Reach above the trunk. Use the `plan`, which may be None.
        self.replicant.reach_for(target={"x": 0, "y": 1.1, "z": table_z},
                                 arm=Arm.right,
                                 plan=plan,
                                 from_held=True,
                                 duration=2)
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
