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
                # The Magnebot finished grasping the target object. Move away from the cabinet.
                elif magnebot_state == MagnebotState.grasping_target:
                    magnebot_state = MagnebotState.moving_away_from_cabinet
                    magnebot.move_by(distance=-1)
                # The Magnebot finished moving away from the cabinet. Reset the arm.
                elif magnebot_state == MagnebotState.moving_away_from_cabinet:
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
