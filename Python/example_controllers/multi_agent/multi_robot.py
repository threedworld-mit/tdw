from enum import Enum
from typing import Dict, Union, List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.librarian import RobotLibrarian, RobotRecord
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class State(Enum):
    idle = 1  # The robot isn't moving.
    swinging = 2  # The robot is rotating its shoulder.
    resetting = 4  # The robot is resetting to its neutral position.


class SwingRobot(Robot):
    def __init__(self, name: str, target_id: int, swing_direction: int, robot_id: int = 0,
                 position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 source: Union[RobotLibrarian, RobotRecord, str] = None):
        super().__init__(name=name, robot_id=robot_id, position=position, rotation=rotation, source=source)
        self.state: State = State.idle
        self.target_id: int = target_id
        self.swing_direction: int = swing_direction

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        # If the robot is idle and collides with the ball,
        if self.state == State.idle:
            # Are any of my joints currently colliding with the target object?
            for collision in self.dynamic.collisions_with_objects:
                # `collision` is a tuple. The first element is always a joint ID and the second element is always an object ID.
                if collision[1] == self.target_id:
                    self.start_to_swing()
        elif self.state == State.swinging:
            if not self.joints_are_moving():
                self.start_to_reset()
        elif self.state == State.resetting:
            if not self.joints_are_moving():
                self.state = State.idle

    def start_to_swing(self) -> None:
        self.state = State.swinging
        self.set_joint_targets(targets={self.static.joint_ids_by_name["shoulder_link"]: 70 * self.swing_direction})

    def start_to_reset(self) -> None:
        self.state = State.resetting
        self.set_joint_targets(targets={self.static.joint_ids_by_name["shoulder_link"]: 0})


class MultiRobot(Controller):
    """
    Two "Swing Robots" swing at a ball when they detect a collision.
    """

    def run(self) -> None:
        object_id = self.get_unique_id()
        # Add two robots, a camera, and image capture.
        robot_0 = SwingRobot(name="ur5",
                             target_id=object_id,
                             swing_direction=-1,
                             robot_id=self.get_unique_id(),
                             position={"x": -1, "y": 0, "z": 0.8})
        robot_1 = SwingRobot(name="ur10",
                             robot_id=self.get_unique_id(),
                             target_id=object_id,
                             swing_direction=1,
                             position={"x": 0.1, "y": 0, "z": -0.5},
                             rotation={"x": 0, "y": 30, "z": 0})
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 0, "y": 3.05, "z": 2.1},
                                   look_at={"x": 0, "y": 0, "z": 0})
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_robot")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([robot_0, robot_1, camera, capture])
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(self.get_add_physics_object(object_id=object_id,
                                                    model_name="prim_sphere",
                                                    library="models_special.json",
                                                    position={"x": 0.36, "y": 0, "z": 0.67},
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                                    default_physics_values=False,
                                                    scale_mass=False,
                                                    mass=5))
        self.communicate(commands)
        while robot_0.joints_are_moving() or robot_1.joints_are_moving():
            self.communicate([])
        # Start swinging.
        robot_1.start_to_swing()
        # Enable collision detection.
        self.communicate({"$type": "send_collisions",
                          "enter": True,
                          "stay": False,
                          "exit": False,
                          "collision_types": ["obj", "env"]})
        for i in range(500):
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MultiRobot()
    c.run()
