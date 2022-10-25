from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class AnimateCollisionDetection(Controller):
    """
    A minimal demo of how collision detection parameters affect animations.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = Replicant()
        self.camera = ThirdPersonCamera(position={"x": -0.5, "y": 1.175, "z": 3},
                                        look_at={"x": 0, "y": 1, "z": 0},
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_animate_collision_detection")
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
                                                    position={"x": -1.5, "y": 0, "z": -0.1},
                                                    rotation={"x": 0, "y": 30, "z": 0})])
        self.camera.look_at(target=self.replicant.replicant_id)

    def dance(self):
        self.replicant.animate(animation="dancing_3")
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])
        print(self.replicant.action.status)


if __name__ == "__main__":
    c = AnimateCollisionDetection()
    c.initialize_scene()
    print("Trying to dance with default collision detection:")
    c.dance()
    print("Trying to ignore the rh10 model:")
    c.replicant.collision_detection.exclude_objects.append(c.object_id_0)
    c.dance()
    print("Trying to ignore the previous animation:")
    c.replicant.collision_detection.previous_was_same = False
    c.dance()
    print("Trying to ignore all objects:")
    c.replicant.collision_detection.objects = False
    c.dance()
    c.communicate({"$type": "terminate"})
