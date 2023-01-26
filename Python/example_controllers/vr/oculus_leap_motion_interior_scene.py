from json import loads
import random
from pathlib import Path
from platform import system
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.backend.platforms import SYSTEM_TO_S3


class OculusTouchProcGen(Controller):
    """
   Interact with objects in VR.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        self.communicate({"$type": "set_screen_size", "width": 1920, "height": 1080})
        # Load the commands used to initialize the objects in the scene.
        init_commands_text = Path("interior_scene.json").read_text()
        # Replace the URL platform infix.
        init_commands_text = init_commands_text.replace("/windows/", "/" + SYSTEM_TO_S3[system()] + "/")
        # Load the commands as a list of dictionaries.
        self.init_commands = loads(init_commands_text)
        # Create the scene lighting add-on.
        self.interior_scene_lighting = InteriorSceneLighting()

        # The ID of the table, as defined in "interior_scene.json".
        self.table_id = 12132217

        # Add the VR rig.
        #self.vr = OculusTouch(human_hands=False, output_data=True, attach_avatar=False, set_graspable=True, non_graspable=[12132217])
        self.vr = OculusLeapMotion(attach_avatar=False, set_graspable=True, non_graspable=[12132217])
        # Quit when the left menu button is pressed.
        #self.vr.listen_to_button(button=OculusTouchButton.primary_button, is_left=True, function=self.quit)

        # Append the add-ons.
        self.add_ons.extend([self.interior_scene_lighting, self.vr])
        # Get a list of HDRI skybox names.
        self.hdri_skybox_names = list(InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES.keys())


    def run(self) -> None:
        # Set the HDRI skybox to a nice sunset one.
        self.interior_scene_lighting.reset(hdri_skybox=self.hdri_skybox_names[4])
        # Load the scene, populate with objects.
        self.communicate(self.init_commands)
        # Start by the table.
        self.vr.set_position({"x": 0.7, "y": 0.0, "z": 1.0})
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = OculusTouchProcGen()
    c.run()
        

