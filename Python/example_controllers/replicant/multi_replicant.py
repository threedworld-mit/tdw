from enum import Enum
from typing import List, Union, Dict, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import OutputData, NavMeshPath, Replicants
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.add_ons.replicant import Replicant
from tdw.replicant.actions.action import Action
from tdw.replicant.actions.move_to import MoveTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency


class NavigateState(Enum):
    getting_path = 1
    navigating = 2
    yielding = 3


class Navigate(Action):
    """
    Navigate using a NavMeshPath and multiple MoveTo child actions.
    """

    def __init__(self, target: Union[Dict[str, float], np.ndarray], collision_detection: CollisionDetection):
        super().__init__()
        # My collision detection. This will be used to instantiate MoveTo child actions.
        self.collision_detection: CollisionDetection = collision_detection
        # Convert the target position to a dictionary if needed.
        if isinstance(target, np.ndarray):
            self.target: Dict[str, float] = TDWUtils.array_to_vector3(target)
        elif isinstance(target, dict):
            self.target = target
        else:
            raise Exception(target)
        # We are getting the path.
        self.navigate_state: NavigateState = NavigateState.getting_path
        # My path.
        self.path: np.ndarray = np.zeros(shape=0)
        # The index of the current waypoint in the path. The point at index=0 is the current position.
        self.path_index: int = 1
        # My MoveTo action.
        self.move_to: Optional[MoveTo] = None
        # My MoveBy action.
        self.move_by: Optional[MoveBy] = None
        # The ImageFrequency. This will be used to instantiate MoveTo child actions.
        # This will be set in get_initialization_commands()
        self.image_frequency: ImageFrequency = ImageFrequency.once
        # Don't try to detect obstacles while pathfinding.
        self.original_avoid: bool = self.collision_detection.avoid
        self.collision_detection.avoid = False

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Remember the ImageFrequency because we'll need it to instantiate MoveTo child actions.
        self.image_frequency = image_frequency
        # Get the usual initialization commands.
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Request a NavMeshPath. Set the path's ID to the Replicant's ID so we know whose path this is.
        commands.append({"$type": "send_nav_mesh_path",
                         "origin": TDWUtils.array_to_vector3(dynamic.transform.position),
                         "destination": self.target,
                         "id": static.replicant_id})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Get my path.
        if self.navigate_state == NavigateState.getting_path:
            # We are now navigating.
            self.navigate_state = NavigateState.navigating
            # Parse the output data.
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Got NavMeshPath data.
                if r_id == "path":
                    path = NavMeshPath(resp[i])
                    # This is my path.
                    if path.get_id() == static.replicant_id:
                        # We failed to pathfind to this destination.
                        if path.get_state() != "complete":
                            self.status = ActionStatus.failed_to_move
                            return []
                        # This is a valid path.
                        else:
                            self.path = path.get_path()
                            # Start moving.
                            return self.set_move_to(resp=resp, static=static, dynamic=dynamic)
        # Continue to navigate.
        elif self.navigate_state == NavigateState.navigating:
            # Check if a Replicant is too close. If so, end the move action and wait.
            close_to_replicant = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Got NavMeshPath data.
                if r_id == "repl":
                    replicants = Replicants(resp[i])
                    for j in range(replicants.get_num()):
                        replicant_id = replicants.get_id(j)
                        # This is me.
                        if replicant_id == static.replicant_id:
                            continue
                        # Get the distance between me and the other Replicant.
                        distance = np.linalg.norm(dynamic.transform.position - replicants.get_position(j))
                        # We're too close. The Replicant with the lower ID should yield.
                        if distance < 0.4 and static.replicant_id < replicant_id:
                            close_to_replicant = True
                            break
                    break
            # We're close to the Replicant.
            if close_to_replicant:
                # We are yielding.
                self.navigate_state = NavigateState.yielding
                # End the MoveTo action.
                commands = []
                if self.move_to is not None:
                    commands.extend(self.move_to.get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                                                  image_frequency=self.image_frequency))
                    # Stop moving.
                    self.move_to = None
                # Start moving backwards.
                self.move_by = MoveBy(distance=-0.5,
                                      dynamic=dynamic,
                                      collision_detection=self.collision_detection,
                                      reset_arms=True,
                                      reset_arms_duration=0.25,
                                      arrived_at=0.1,
                                      max_walk_cycles=100,
                                      previous=None)
                # Initialize the MoveBy child action.
                commands.extend(self.move_by.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                                         image_frequency=self.image_frequency))
                return commands
            # Get the child action's ongoing commands. This will also update the child action's status.
            commands = self.move_to.get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
            # The child action ended in success. Check if this is the last waypoint.
            if self.move_to.status == ActionStatus.success:
                # We arrived at the destination.
                if self.path_index >= self.path.shape[0]:
                    self.status = ActionStatus.success
                    return commands
                # Move to the next waypoint.
                else:
                    # End the current move_to action.
                    commands.extend(self.move_to.get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                                                  image_frequency=self.image_frequency))
                    # Start a new move_to action. Append the new child action's initialization commands.
                    commands.extend(self.set_move_to(resp=resp, static=static, dynamic=dynamic))
            # The action ended in failure.
            elif self.move_to.status != ActionStatus.ongoing:
                self.status = self.move_to.status
            return commands
        # Continue to yield by backing up.
        elif self.navigate_state == NavigateState.yielding:
            commands = self.move_by.get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
            # Keep yielding.
            if self.move_by.status == ActionStatus.ongoing:
                return commands
            # We're done yield.
            else:
                # We need to get a new path.
                self.navigate_state = NavigateState.getting_path
                self.path_index -= 1
                # End the MoveBy action.
                commands.extend(self.move_by.get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                                              image_frequency=self.image_frequency))
                # Start getting a new path.
                commands.extend(self.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                                 image_frequency=self.image_frequency))
                return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        # Reset obstacle avoidance.
        self.collision_detection.avoid = self.original_avoid
        # Get end commands.
        if self.move_to is not None:
            return self.move_to.get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                                 image_frequency=image_frequency)
        else:
            return super().get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                            image_frequency=image_frequency)

    def set_move_to(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Set the action.
        self.move_to = MoveTo(target=self.path[self.path_index],
                              collision_detection=self.collision_detection,
                              reset_arms=True,
                              reset_arms_duration=0.25,
                              arrived_at=0.1,
                              max_walk_cycles=100,
                              bounds_position="center",
                              previous=None)
        # Update the path index.
        self.path_index += 1
        # Return the initialization commands.
        return self.move_to.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                        image_frequency=self.image_frequency)


class Pathfind(Controller):
    """
    An example of how to utilize the NavMesh to pathfind.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant_0 = Replicant(position={"x": 0.1, "y": 0, "z": -5},
                                     replicant_id=0)
        self.replicant_1 = Replicant(position={"x": 0.1, "y": 0, "z": 3},
                                     replicant_id=1)
        self.camera: ThirdPersonCamera = ThirdPersonCamera(position={"x": 0, "y": 13.8, "z": 0},
                                                           look_at={"x": 0, "y": 0, "z": 0},
                                                           avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_replicant_navigate")
        print(f"Images will be saved to: {path}")
        self.capture: ImageCapture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant_0, self.replicant_1, self.camera, self.capture])
        # Set the object IDs.
        self.trunk_id = Controller.get_unique_id()
        self.chair_id = Controller.get_unique_id()
        self.table_id = Controller.get_unique_id()
        self.rocking_horse_id = Controller.get_unique_id()

    def init_scene(self):
        # Load the scene.
        # Bake the NavMesh.
        # Add objects to the scene and add NavMesh obstacles.
        self.communicate([{"$type": "load_scene",
                           "scene_name": "ProcGenScene"},
                          TDWUtils.create_empty_room(12, 12),
                          {"$type": "bake_nav_mesh"},
                          Controller.get_add_object(model_name="trunck",
                                                    object_id=self.trunk_id,
                                                    position={"x": 1.5, "y": 0, "z": 0}),
                          {"$type": "make_nav_mesh_obstacle",
                           "id": self.trunk_id,
                           "carve_type": "stationary"},
                          Controller.get_add_object(model_name="chair_billiani_doll",
                                                    object_id=self.chair_id,
                                                    position={"x": -2.25, "y": 0, "z": 2.5},
                                                    rotation={"x": 0, "y": 20, "z": 0}),
                          {"$type": "make_nav_mesh_obstacle",
                           "id": self.chair_id,
                           "carve_type": "stationary"},
                          Controller.get_add_object(model_name="live_edge_coffee_table",
                                                    object_id=self.table_id,
                                                    position={"x": 0.2, "y": 0, "z": -2.25},
                                                    rotation={"x": 0, "y": 20, "z": 0}),
                          {"$type": "make_nav_mesh_obstacle",
                           "id": self.table_id,
                           "carve_type": "stationary"},
                          Controller.get_add_object(model_name="rh10",
                                                    object_id=self.rocking_horse_id,
                                                    position={"x": -1, "y": 0, "z": 1.5}),
                          {"$type": "make_nav_mesh_obstacle",
                           "id": self.rocking_horse_id,
                           "carve_type": "stationary"}])

    def run(self, replicant_0_target: Dict[str, float], replicant_1_target: Dict[str, float]) -> None:
        # Initialize the scene.
        self.init_scene()
        done = False
        self.replicant_0.collision_detection.exclude_objects.append(self.replicant_1.replicant_id)
        self.replicant_1.collision_detection.exclude_objects.append(self.replicant_0.replicant_id)
        # Tell both Replicants to start to navigate.
        self.replicant_0.action = Navigate(target=replicant_0_target,
                                           collision_detection=self.replicant_0.collision_detection)
        self.replicant_1.action = Navigate(target=replicant_1_target,
                                           collision_detection=self.replicant_1.collision_detection)
        while not done:
            done = True
            for replicant, target in zip([self.replicant_0, self.replicant_1], [replicant_0_target, replicant_1_target]):
                # At least one Replicant is still moving. We're not done.
                if replicant.action.status == ActionStatus.ongoing:
                    done = False
                # The Replicant's action ended. Check if it was a Navigate action.
                elif replicant.action.status == ActionStatus.success:
                    # If the action that just ended was a MoveBy, start navigating. We're not done.
                    if isinstance(replicant.action, MoveBy):
                        done = False
                        # Start navigating.
                        replicant.action = Navigate(target=target, collision_detection=replicant.collision_detection)
                # The Replicant's action failed. We're not done.
                else:
                    done = False
                    # If the navigation failed, try walking forward. We're not done.
                    if isinstance(replicant.action, Navigate):
                        replicant.action = MoveBy(distance=0.5,
                                                  dynamic=replicant.dynamic,
                                                  collision_detection=replicant.collision_detection,
                                                  reset_arms=True,
                                                  reset_arms_duration=0.25,
                                                  arrived_at=0.1,
                                                  max_walk_cycles=100,
                                                  previous=None)
                    else:
                        # Start navigating.
                        replicant.action = Navigate(target=target, collision_detection=replicant.collision_detection)
            # Update the simulation state.
            self.communicate([])
        # End.
        self.end()

    def end(self) -> None:
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Pathfind()
    c.run(replicant_0_target={"x": 0, "y": 0, "z": 4},
          replicant_1_target={"x": -1, "y": 0, "z": -3})

