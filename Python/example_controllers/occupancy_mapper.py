from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class OccupancyMapper(Controller):
    """
    Generate occupancy maps in a simple scene_data populated by objects.
    For more information, [read this](add_ons/occupancy_map.md).
    """

    def run(self) -> None:
        """
        Create a simple scene_data. Generate some occupancy maps and capture images of the scene_data and occupancy map.
        """

        self.start()
        o = OccupancyMap()
        self.add_ons.append(o)
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_object(model_name="rh10",
                                              position={"x": 1, "y": 0, "z": -3.6},
                                              object_id=self.get_unique_id()),
                         self.get_add_object(model_name="trunck",
                                             position={"x": 4, "y": 0, "z": 1.3},
                                             rotation={"x": 0, "y": -28, "z": 0},
                                             object_id=self.get_unique_id())])
        o.generate()
        self.communicate([])
        cam = ThirdPersonCamera(position={"x": 0, "y": 14, "z": 0},
                                look_at=TDWUtils.VECTOR3_ZERO)
        cap = ImageCapture(avatar_ids=[cam.avatar_id], path=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("occupancy_mapper"))
        print(f"Images will be saved to: {cap.path}")
        self.add_ons.extend([cam, cap])
        # Generate an image of the scene_data.
        self.communicate([])
        # Generate an image of the scene_data with blue squares marking the occupancy map.
        o.show()
        self.communicate([])
        # Generate an image of the scene_data and hide the occupancy map again.
        o.hide()
        self.communicate([])

        # Add a new object. Regenerate the occupancy map and show the free spaces.
        self.communicate(self.get_add_object(model_name="iron_box",
                                             position={"x": -3, "y": 0, "z": 2.3},
                                             rotation={"x": 0, "y": 70, "z": 0},
                                             object_id=self.get_unique_id()))
        o.generate()
        self.communicate([])
        o.show()
        self.communicate([])
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = OccupancyMapper(launch_build=False)
    c.run()
