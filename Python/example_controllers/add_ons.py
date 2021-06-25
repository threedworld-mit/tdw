from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.debug import Debug
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera


class AddOns(Controller):
    """
    Add multiple add-ons to a controller.
    """

    def run(self) -> None:
        self.start()
        object_id = 0
        path = "D:/add_ons_images"

        # Create a Debug add-on.
        debug = Debug(record=True, path=path + "/log.json")

        # Create a third-person camera that will look at the target object.
        camera = ThirdPersonCamera(position={"x": -1, "y": 1.5, "z": 0.4},
                                   look_at=object_id)

        # Create an image capture add-on to save images per-frame.
        capture = ImageCapture(path=path,
                               avatar_ids=[camera.avatar_id])

        # Add all of the add-ons.
        self.add_ons.extend([debug, camera, capture])

        # Create a room and add an object.
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_object(model_name="iron_box",
                                              object_id=object_id),
                          {"$type": "apply_force_to_object",
                           "id": object_id,
                           "force": {"x": 0, "y": 4, "z": 8}}])

        # Let the simulation run. Images will be saved to disk.
        for i in range(200):
            self.communicate([])

        # Stop the build. This will generate a log file.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = AddOns(launch_build=False)
    c.run()
