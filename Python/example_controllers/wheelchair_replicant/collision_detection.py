from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class CollisionDetection(Controller):
    """
    A minimal demo of how collision detection parameters affect agent movement.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = WheelchairReplicant(position={"x": -3, "y": 0, "z": 0},
                                             rotation={"x": 0, "y": 90, "z": 0})
        self.camera = ThirdPersonCamera(position={"x": -0.5, "y": 1.175, "z": 3},
                                        look_at={"x": 0, "y": 1, "z": 0},
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_collision_detection")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.replicant, self.camera, self.capture])
        self.object_id_0 = Controller.get_unique_id()
        self.object_id_1 = Controller.get_unique_id()

    def initialize_scene(self):
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          Controller.get_add_object(model_name="rh10",
                                                    object_id=self.object_id_0,
                                                    position={"x": -0.6, "y": 0, "z": 0.01}),
                          Controller.get_add_object(model_name="chair_billiani_doll",
                                                    object_id=self.object_id_1,
                                                    position={"x": -1.5, "y": 0, "z": 0},
                                                    rotation={"x": 0, "y": 30, "z": 0})])
        self.camera.look_at(target=self.replicant.replicant_id)

    def move(self):
        self.replicant.move_by(distance=2)
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])
        print(self.replicant.action.status)


if __name__ == "__main__":
    c = CollisionDetection()
    c.initialize_scene()
    print("Trying to move with default collision detection:")
    c.move()
    print("Trying to ignore the rh10 model:")
    c.replicant.collision_detection.exclude_objects.append(c.object_id_0)
    c.move()
    print("Trying to ignore the previous movement:")
    c.replicant.collision_detection.previous_was_same = False
    c.move()
    print("Trying to ignore all objects:")
    c.replicant.collision_detection.objects = False
    c.replicant.collision_detection.avoid = False
    c.move()
    c.communicate({"$type": "terminate"})
