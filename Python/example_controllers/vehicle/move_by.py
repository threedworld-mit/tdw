import numpy as np
from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class MoveBy(Controller):
    """
    Drive forward by a distance.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vehicle = Vehicle(rotation={"x": 0, "y": -90, "z": 0}, image_passes=["_img"])
        self.add_ons.append(self.vehicle)
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_dynamic_data")

    def move_by(self, distance: float):
        # Get the initial position.
        p0: np.ndarray = np.copy(self.vehicle.dynamic.transform.position)
        self.vehicle.set_drive(1)
        # Drive until the vehicle exceeds the distance.
        while np.linalg.norm(p0 - self.vehicle.dynamic.transform.position) < distance:
            self.communicate([])
        # Brake until the vehicle stops moving.
        self.vehicle.set_drive(0)
        self.vehicle.set_brake(1)
        while np.linalg.norm(self.vehicle.dynamic.rigidbody.velocity) > 0.01:
            self.communicate([])
        print(np.linalg.norm(p0 - self.vehicle.dynamic.transform.position))

    def run(self):
        self.communicate(c.get_add_scene(scene_name="suburb_scene_2023"))
        self.move_by(6)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = MoveBy()
    c.run()
