from json import loads
from pathlib import Path
from platform import system
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.backend.platforms import SYSTEM_TO_S3


class InteriorScene(Controller):
    """
    Load an interior scene populated with objects. Render images of the scene using each interior lighting HDRI skybox.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate({"$type": "set_screen_size",
                          "width": 512,
                          "height": 512})
        # Load the commands used to initialize the objects in the scene.
        init_commands_text = Path("interior_scene.json").read_text()
        # Replace the URL platform infix.
        init_commands_text = init_commands_text.replace("/windows/", "/" + SYSTEM_TO_S3[system()] + "/")
        # Load the commands as a list of dictionaries.
        self.init_commands = loads(init_commands_text)
        # Set the camera. The position and rotation of the camera doesn't change between scenes.
        self.camera: ThirdPersonCamera = ThirdPersonCamera(avatar_id="a",
                                                           position={"x": -0.6771, "y": 1.5, "z": 2.0463},
                                                           rotation={"x": 0.0177, "y": 0.9814, "z": -0.1123, "w": 0.1545})
        # Enable image capture.
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("interior_scene")
        print(f"Images will be saved to: {self.path}")
        self.capture: ImageCapture = ImageCapture(avatar_ids=["a"], path=self.path, pass_masks=["_img"])
        # Create the scene lighting add-on.
        self.interior_scene_lighting = InteriorSceneLighting()
        # Append the add-ons.
        self.add_ons.extend([self.interior_scene_lighting, self.camera, self.capture])
        # Get a list of HDRI skybox names.
        self.hdri_skybox_names = list(InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES.keys())

    def show_skybox(self, hdri_skybox_index: int) -> None:
        # Reset the add-ons.
        self.camera.initialized = False
        self.capture.initialized = False
        # Set the next HDRI skybox.
        self.interior_scene_lighting.reset(hdri_skybox=self.hdri_skybox_names[hdri_skybox_index])
        # Load the scene, populate with objects, add the camera, set the skybox and post-processing, and capture an image.
        self.communicate(self.init_commands)
        # Rename the image to the name of the skybox.
        src_filename = "a/img_" + str(self.capture.frame - 1).zfill(4) + ".jpg"
        dst_filename = "a/" + self.hdri_skybox_names[hdri_skybox_index] + ".jpg"
        self.path.joinpath(src_filename).replace(self.path.joinpath(dst_filename))

    def show_all_skyboxes(self) -> None:
        for i in range(len(self.hdri_skybox_names)):
            self.show_skybox(hdri_skybox_index=i)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = InteriorScene()
    c.show_all_skyboxes()
