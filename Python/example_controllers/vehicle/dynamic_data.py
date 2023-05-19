from json import dumps
from typing import Union, List
from tdw.controller import Controller
from tdw.add_ons.vehicle import Vehicle
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class DynamicData(Controller):
    """
    Read and save the vehicle's output data, including image data.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        self._first_time_only = True
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vehicle = Vehicle(rotation={"x": 0, "y": -90, "z": 0}, image_passes=["_img"])
        self.add_ons.append(self.vehicle)
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vehicle_dynamic_data")
        print(f"Images and JSON data will be saved to: {self.path}")
        # Start the json data.
        self.output_data = list()

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        resp = super().communicate(commands=commands)
        if self._first_time_only:
            self._first_time_only = False
            return resp
        # Save the vehicle's images.
        self.vehicle.dynamic.save_images(output_directory=self.path)
        # Write the other data as a JSON file.
        output_data = {"transform": {"position": self.vehicle.dynamic.transform.position.tolist(),
                                     "rotation": self.vehicle.dynamic.transform.rotation.tolist(),
                                     "forward": self.vehicle.dynamic.transform.forward.tolist()},
                       "camera_matrices": {"camera_matrix": self.vehicle.dynamic.camera_matrix.tolist(),
                                           "projection_matrix": self.vehicle.dynamic.projection_matrix.tolist()}}
        # Remember the output data.
        self.output_data.append(output_data)
        # Return the response from the build.
        return resp

    def run(self):
        self.communicate(c.get_add_scene(scene_name="suburb_scene_2023"))
        # Drive the vehicle forward.
        self.vehicle.set_drive(0.5)
        while self.vehicle.dynamic.transform.position[0] > -30:
            self.communicate([])
        # Brake.
        self.vehicle.set_drive(0)
        self.vehicle.set_brake(0.7)
        for i in range(100):
            c.communicate([])
        # Quit.
        self.communicate({"$type": "terminate"})
        # Write the JSON data.
        self.path.joinpath("output_data.json").write_text(dumps(self.output_data, indent=2))


if __name__ == "__main__":
    c = DynamicData()
    c.run()
