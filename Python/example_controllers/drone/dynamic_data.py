from json import dumps
from typing import Union, List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.drone import Drone
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class DynamicData(Controller):
    """
    Read and save the drone's output data, including image data.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.drone = Drone(position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": -90, "z": 0})
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("drone_dynamic_data")
        print(f"Images and JSON data will be saved to: {self.path}")
        # Start the json data.
        self.output_data = list()

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        resp = super().communicate(commands=commands)
        # Save the drone's images.
        self.drone.dynamic.save_images(output_directory=self.path)
        # Write the other data as a JSON file.
        output_data = {"transform": {"position": self.drone.dynamic.transform.position.tolist(),
                                     "rotation": self.drone.dynamic.transform.rotation.tolist(),
                                     "forward": self.drone.dynamic.transform.forward.tolist()},
                       "camera_matrices": {"camera_matrix": self.drone.dynamic.camera_matrix.tolist(),
                                           "projection_matrix": self.drone.dynamic.projection_matrix.tolist()},
                       "raycast": {"hit": self.drone.dynamic.raycast_hit,
                                   "point": self.drone.dynamic.raycast_point.tolist()},
                       "motor_on": self.drone.dynamic.motor_on}
        # Remember the output data.
        self.output_data.append(output_data)
        # Return the response from the build.
        return resp

    def run(self):
        self.communicate([TDWUtils.create_empty_room(12, 12)])
        for i in range(200):
            self.communicate([])
        # Let the drone rise.
        self.drone.set_lift(1)
        while self.drone.dynamic.transform.position[1] < 10:
            self.communicate([])
        # Quit.
        self.communicate({"$type": "terminate"})
        # Write the JSON data.
        self.path.joinpath("output_data.json").write_text(dumps(self.output_data, indent=2))


if __name__ == "__main__":
    c = DynamicData()
    c.run()
