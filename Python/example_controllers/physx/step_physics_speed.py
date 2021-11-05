from time import time
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.step_physics import StepPhysics


class StepPhysicsSpeed(Controller):
    """
    Compare the speed of a simulation without skipping physics frames vs. skipping physics frames.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Add a camera and an object manager.
        self.object_manager: ObjectManager = ObjectManager(transforms=False, rigidbodies=True)
        camera = ThirdPersonCamera(position={"x": 3, "y": 2.5, "z": -1},
                                   look_at={"x": 0, "y": 0, "z": 0})
        self.add_ons.extend([self.object_manager, camera])
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def trial(self) -> float:
        """
        Wait for an object to fall.

        :return: The elapsed time.
        """

        object_id = self.get_unique_id()
        # Reset the object manager.
        self.object_manager.initialized = False
        # Add the object.
        self.communicate(self.get_add_physics_object(model_name="iron_box",
                                                     object_id=object_id,
                                                     position={"x": 0, "y": 30, "z": 0}))
        t0 = time()
        # Wait for the object to fall.
        while not self.object_manager.rigidbodies[object_id].sleeping:
            self.communicate([])
        t1 = time() - t0
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return t1

    def run(self) -> None:
        t_no_skip = self.trial()
        # Add a StepPhysics add-on.
        self.add_ons.append(StepPhysics(num_frames=10))
        t_skip_frames = self.trial()
        print(t_no_skip, t_skip_frames)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = StepPhysicsSpeed()
    c.run()
