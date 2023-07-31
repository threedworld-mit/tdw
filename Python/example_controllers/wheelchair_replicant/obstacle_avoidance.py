from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ObstacleAvoidance(Controller):
    """
    A very simple method for navigating around obstacles.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Set the target object's ID here so it can be referenced from more than one function.
        self.target_id = Controller.get_unique_id()
        # Set the replicant here so that it can be referenced from more than one function.
        self.replicant = WheelchairReplicant(position={"x": 0, "y": 0, "z": -8},
                                             image_frequency=ImageFrequency.never)

    def run(self) -> None:
        # Enable image capture from a third-person camera.
        camera = ThirdPersonCamera(position={"x": -0.5, "y": 1.175, "z": 8.45},
                                   look_at={"x": 0.5, "y": 1, "z": 0},
                                   avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_obstacle_avoidance")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], path=path)
        self.add_ons.extend([self.replicant, camera, capture])
        # Create an empty room.
        commands = [TDWUtils.create_empty_room(12, 20)]
        # Add some objects.
        commands.extend(Controller.get_add_physics_object(model_name="chair_billiani_doll",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 1.35, "y": 0, "z": 2.75},
                                                          rotation={"x": 0, "y": 20, "z": 0},
                                                          library="models_core.json"))
        commands.extend(Controller.get_add_physics_object(model_name="live_edge_coffee_table",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 0, "z": 2},
                                                          rotation={"x": 0, "y": 20, "z": 0},
                                                          library="models_core.json"))
        # Add a ball.
        ball_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name="prim_sphere",
                                                          object_id=ball_id,
                                                          position={"x": 5, "y": 0, "z": 3.5},
                                                          rotation={"x": 0, "y": 0, "z": 0},
                                                          scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                          kinematic=True,
                                                          gravity=False,
                                                          library="models_special.json"))
        # Add the target object.
        commands.extend(Controller.get_add_physics_object(model_name="prim_sphere",
                                                          object_id=self.target_id,
                                                          position={"x": 0, "y": 0, "z": 4.0},
                                                          rotation={"x": 0, "y": 0, "z": 0},
                                                          scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                          kinematic=True,
                                                          gravity=False,
                                                          library="models_special.json"))
        # Send the commands.
        self.communicate(commands)
        # Exclude the balls so they do not act as obstacles and trigger the avoidance mechanisms.
        self.replicant.collision_detection.exclude_objects = [self.target_id, ball_id]
        # Ignore this because we want to move the Replicant after hitting an obstacle.
        self.replicant.collision_detection.previous_was_same = False
        # Start to navigate.
        done = False
        while not done:
            # Move to the target.
            self.replicant.move_to(target=self.target_id)
            self.do_action()
            # We arrived at the target.
            if self.replicant.action.status == ActionStatus.success:
                done = True
            # Take evasive action.
            else:
                self.replicant.collision_detection.avoid = False
                self.replicant.move_by(distance=-1)
                self.do_action()
                self.replicant.turn_by(angle=45.0)
                self.do_action()
                self.replicant.move_by(distance=3.0)
                self.do_action()
                self.replicant.collision_detection.avoid = True
        self.communicate({"$type": "terminate"})

    def do_action(self) -> None:
        """
        Call `communicate([])` until the Replicant's action is done.
        """

        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])


if __name__ == "__main__":
    ObstacleAvoidance().run()
