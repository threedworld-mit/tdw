from typing import Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import OutputData, NavMeshPath
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus


class Pathfind(Controller):
    """
    An example of how to utilize the NavMesh to pathfind.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = Replicant(position={"x": 0.1, "y": 0, "z": -5})
        self.camera: ThirdPersonCamera = ThirdPersonCamera(position={"x": 0, "y": 13.8, "z": 0},
                                                           look_at={"x": 0, "y": 0, "z": 0},
                                                           avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_pathfind")
        print(f"Images will be saved to: {path}")
        self.capture: ImageCapture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant, self.camera, self.capture])
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

    def navigate(self, destination: Dict[str, float]) -> bool:
        # Don't handle collision detection (it will interfere with NavMesh pathfinding).
        self.replicant.collision_detection.avoid = False
        # The origin of the path is the current position of the Replicant.
        origin = TDWUtils.array_to_vector3(self.replicant.dynamic.transform.position)
        # Request a NavMeshPath.
        resp = self.communicate({"$type": "send_nav_mesh_path",
                                 "origin": origin,
                                 "destination": destination,
                                 "id": self.replicant.replicant_id})
        # Parse the output data to get the path.
        path: np.ndarray = np.zeros(shape=1)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "path":
                nav_mesh_path = NavMeshPath(resp[i])
                # This path belongs to the Replicant (this is useful when there is more than one agent).
                if nav_mesh_path.get_id() == self.replicant.replicant_id:
                    # We failed to get a valid path.
                    if nav_mesh_path.get_state() != "complete":
                        self.replicant.collision_detection.avoid = True
                        return False
                    # Get the path.
                    path = nav_mesh_path.get_path()
                    # Break because we have the data we need.
                    break
        # Move to each waypoint. Ignore the first waypoint because it's the position of the Replicant.
        for i in range(1, path.shape[0]):
            target = TDWUtils.array_to_vector3(path[i])
            target["y"] = 0
            # Move to the waypoint.
            self.replicant.move_to(target=target)
            # Do the action.
            self.do_action()
            # If the Replicant failed to reach the waypoint, end here.
            if self.replicant.action.status != ActionStatus.success:
                self.replicant.collision_detection.avoid = True
                return False
        # We arrived at the destination. Re-enable obstacle detection and return True.
        self.replicant.collision_detection.avoid = True
        return True

    def do_action(self) -> None:
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])

    def end(self) -> None:
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Pathfind()
    # Initialize the scene.
    c.init_scene()
    # Navigate to a destination.
    success = c.navigate(destination={"x": 0, "y": 0, "z": 4})
    print(success)
    # End the simulation.
    c.end()
