import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, NavMeshPath, Bounds
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.arm import Arm
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class CarryCouch(Controller):
    """
    Both Replicants will approach opposite sides of the sofa.
    They will reach to lift up the sofa (although only one Replicant is grasp), carry the sofa, and put it down again.

    In some cases, the Replicants will act asynchronously.
    In some cases, the Replicants will wait for each other to finish their respective actions.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Set the object ID.
        self.object_id: int = Controller.get_unique_id()
        # Set the Replicants.
        self.replicant_0: Replicant = Replicant(replicant_id=0, position={"x": -1, "y": 0, "z": -1})
        self.replicant_1: Replicant = Replicant(replicant_id=1, position={"x": 1, "y": 0, "z": -1})
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(position={"x": 0, "y": 2.2, "z": -2.61},
                                   avatar_id="a",
                                   look_at=self.object_id)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_carry_couch")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant_0, self.replicant_1, camera, capture])
        # Initialize the scene.
        commands = [TDWUtils.create_empty_room(12, 12),
                    {"$type": "bake_nav_mesh",
                     "ignore": [0, 1]},
                    {"$type": "set_target_framerate",
                     "framerate": 30}]
        commands.extend(Controller.get_add_physics_object(model_name="arflex_strips_sofa",
                                                          object_id=self.object_id,
                                                          position={"x": 0, "y": 0, "z": 1}))
        self.communicate(commands)

    def carry_sofa(self) -> None:
        """
        A "meta-action" directing both Replicants to "carry" a sofa.
        """

        # Get a response from the build.
        resp = self.communicate([])
        # Get the left and right sides of the sofa.
        left = np.zeros(shape=3)
        right = np.zeros(shape=3)
        center = np.zeros(shape=3)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "boun":
                bounds = Bounds(resp[i])
                for j in range(bounds.get_num()):
                    if bounds.get_id(j) == self.object_id:
                        left = bounds.get_left(j)
                        right = bounds.get_right(j)
                        center = bounds.get_center(j)
                        break
                break
        # Set the height of each bounds point to 0.
        left[1] = 0
        right[1] = 0
        center[1] = 0
        # Offset the bounds positions.
        v = left - center
        v = v / np.linalg.norm(v)
        left += v * 0.45
        v = right - center
        v = v / np.linalg.norm(v)
        right += v * 0.45
        # Set target positions for each.
        distance_left = np.linalg.norm(self.replicant_0.dynamic.transform.position - left)
        distance_right = np.linalg.norm(self.replicant_0.dynamic.transform.position - right)
        if distance_left < distance_right:
            replicant_0_target = left
            replicant_1_target = right
        else:
            replicant_0_target = right
            replicant_1_target = left
        # Get paths to each target.
        resp = self.communicate([{"$type": "send_nav_mesh_path",
                                  "origin": TDWUtils.array_to_vector3(self.replicant_0.dynamic.transform.position),
                                  "destination": TDWUtils.array_to_vector3(replicant_0_target),
                                  "id": self.replicant_0.replicant_id},
                                 {"$type": "send_nav_mesh_path",
                                  "origin": TDWUtils.array_to_vector3(self.replicant_1.dynamic.transform.position),
                                  "destination": TDWUtils.array_to_vector3(replicant_1_target),
                                  "id": self.replicant_1.replicant_id}])
        # Determine which Replicant requested this path.
        replicant_0_path = np.zeros(shape=0)
        replicant_1_path = np.zeros(shape=0)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "path":
                nav_mesh_path = NavMeshPath(resp[i])
                path_id = nav_mesh_path.get_id()
                if path_id == self.replicant_0.replicant_id:
                    replicant_0_path = nav_mesh_path.get_path()
                elif path_id == self.replicant_1.replicant_id:
                    replicant_1_path = nav_mesh_path.get_path()
        # These are the indices of the current waypoint in each path.
        replicant_0_path_index: int = 1
        replicant_1_path_index: int = 1
        # Start moving to each waypoint.
        self.replicant_0.collision_detection.avoid = False
        self.replicant_1.collision_detection.avoid = False
        self.replicant_0.collision_detection.objects = False
        self.replicant_1.collision_detection.objects = False
        self.replicant_0.move_to(target=replicant_0_path[replicant_0_path_index])
        self.replicant_1.move_to(target=replicant_1_path[replicant_1_path_index])
        # Wait until the Replicants stop pathfinding.
        done = False
        while not done:
            # Check if both Replicants are done navigating.
            replicant_0_done = False
            if self.replicant_0.action.status != ActionStatus.ongoing:
                replicant_0_path_index += 1
                if replicant_0_path_index >= replicant_0_path.shape[0]:
                    replicant_0_done = True
                else:
                    self.replicant_0.move_to(replicant_0_path[replicant_0_path_index], arrived_at=0.05)
            replicant_1_done = False
            if self.replicant_1.action.status != ActionStatus.ongoing:
                replicant_1_path_index += 1
                if replicant_1_path_index >= replicant_1_path.shape[0]:
                    replicant_1_done = True
                else:
                    self.replicant_1.move_to(replicant_1_path[replicant_1_path_index], arrived_at=0.05)
            done = replicant_0_done and replicant_1_done
            # Continue the loop.
            self.communicate([])
        # Look at the sofa's center.
        self.replicant_0.turn_to(target=center)
        self.replicant_1.turn_to(target=center)
        self.do_actions()
        # Reach for the couch.
        self.replicant_0.reach_for(target=self.object_id, arm=[Arm.left, Arm.right])
        self.replicant_1.reach_for(target=self.object_id, arm=[Arm.left, Arm.right])
        self.do_actions()
        # Only the first Replicant grasps the couch.
        self.replicant_0.grasp(target=self.object_id, arm=Arm.left, angle=None)
        self.do_replicant_0_action()
        # Everyone raises their hands.
        self.reach_for_height(y=0.8)
        # Do the actions.
        self.do_actions()
        # The first Replicant walks backwards. The second Replicant walks forwards.
        self.replicant_0.move_by(distance=-2,
                                 reset_arms=False)
        self.replicant_1.move_by(distance=2,
                                 reset_arms=False)
        self.do_actions()
        # Lower the sofa.
        self.reach_for_height(y=0.1)
        # Drop the sofa.
        self.replicant_0.drop(arm=Arm.left)
        self.do_replicant_0_action()
        # Reset the arms.
        self.replicant_0.reset_arm(arm=[Arm.left, Arm.right])
        self.replicant_1.reset_arm(arm=[Arm.left, Arm.right])
        self.do_actions()

    def do_actions(self) -> None:
        """
        Wait for both Replicants' actions to end.
        """

        while self.replicant_0.action.status == ActionStatus.ongoing or self.replicant_1.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])

    def do_replicant_0_action(self) -> None:
        """
        Wait for only the first Replicant's action to end.
        """

        while self.replicant_0.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])

    def reach_for_height(self, y: float) -> None:
        """
        Tell both Replicants to reach for positions relative to their left hands.

        :param y: Add this y value to the target position.
        """

        for replicant in [self.replicant_0, self.replicant_1]:
            # Get the position of the left hand.
            target = TDWUtils.array_to_vector3(replicant.dynamic.body_parts[replicant.static.hands[Arm.left]].position)
            # Raise the target's height.
            target["y"] = y
            # The left hand reaches for the target and the right hand follows.
            replicant.reach_for(target=target,
                                arm=Arm.left,
                                offhand_follows=True)
        # Both Replicants do their actions.
        self.do_actions()


if __name__ == "__main__":
    c = CarryCouch()
    c.carry_sofa()
    c.communicate({"$type": "terminate"})
