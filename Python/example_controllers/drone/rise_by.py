from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class RiseBy(Controller):
    """
    Wrap drone movement in a simple "rise by" function.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.drone = Drone()
        self.camera = ThirdPersonCamera(position={"x": 2.59, "y": 1.2, "z": -3.57},
                                        look_at=self.drone.drone_id,
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("drone_rise_by")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([self.drone, self.camera, self.capture])

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

    def run(self):
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self.rise_by(1.1)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = RiseBy()
    c.run()
