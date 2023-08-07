import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.collision_manager import CollisionManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class CollisionDetection(Controller):
    """
    Drone collision detection.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.drone = Drone()
        self.camera = ThirdPersonCamera(position={"x": 2.59, "y": 1.2, "z": -3.57},
                                        look_at=self.drone.drone_id,
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("drone_collision_detection")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=path)
        self.collision_manager = CollisionManager(enter=True, stay=False, exit=False)
        self.object_id = Controller.get_unique_id()
        self.add_ons.extend([self.drone, self.camera, self.capture, self.collision_manager])

    def rise_by(self, y: float):
        if y > 0:
            self.drone.set_lift(1)
            up = True
        else:
            self.drone.set_lift(-1)
            up = False
        y1 = self.drone.dynamic.transform.position[1] + y
        if up:
            while self.drone.dynamic.transform.position[1] < y1:
                self.communicate([])
        else:
            while self.drone.dynamic.transform.position[1] > y1:
                self.communicate([])
        self.drone.set_lift(0)

    def move_by(self, z: float, arrived_at: float = 0.1):
        if z > 0:
            self.drone.set_drive(1)
        else:
            self.drone.set_drive(-1)
        # Get the target position. We can't use the z coordinate because the drone might have turned.
        target = self.drone.dynamic.transform.position + self.drone.dynamic.transform.forward * z
        # Wait for the drone to reach the target, or stop if there was a collision.
        while len(self.collision_manager.obj_collisions) == 0 and np.linalg.norm(self.drone.dynamic.transform.position - target) > arrived_at:
            self.communicate([])
        # The drone crashed into an obstacle. Set all force values to 0 and let it fall.
        if len(self.collision_manager.obj_collisions) > 0:
            self.drone.set_motor(False)
            print(self.drone.dynamic.motor_on)
            for ids in self.collision_manager.obj_collisions:
                print(ids.int1, ids.int2)
            for i in range(100):
                self.communicate([])
        else:
            self.drone.set_drive(0)

    def run(self):
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=self.object_id,
                                                          library="models_flex.json",
                                                          position={"x": 0, "y": 0, "z": 3},
                                                          scale_factor={"x": 0.5, "y": 3, "z": 0.3},
                                                          kinematic=True))
        self.communicate(commands)
        self.rise_by(1.1)
        self.move_by(5)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = CollisionDetection()
    c.run()
