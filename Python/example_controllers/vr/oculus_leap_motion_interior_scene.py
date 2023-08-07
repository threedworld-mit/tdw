from json import loads
from pathlib import Path
from tdw.controller import Controller
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting


class OculusLeapMotionInteriorScene(Controller):
    """
    Interact with objects in VR with UltraLeap hand tracking in a kitchen scene.

    WARNING! This is not a good example of how to initialize a scene.
    It's meant to showcase VR functionality such that each of our users has the same experience.
    Don't copy+paste this code with interior_scene.json.
    Instead, use the ProcGenKitchen add-on.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate({"$type": "set_screen_size",
                          "width": 512,
                          "height": 512})
        # Load the commands used to initialize the objects in the scene.
        init_commands_text = Path("interior_scene.json").read_text()
        # Load the commands as a list of dictionaries.
        self.init_commands = loads(init_commands_text)
        # Create the scene lighting add-on.
        self.interior_scene_lighting = InteriorSceneLighting()
        # Add the VR rig.
        self.vr = OculusLeapMotion()
        # Append the add-ons.
        self.add_ons.extend([self.interior_scene_lighting, self.vr])

    def run(self) -> None:
        # Set the HDRI skybox to a nice sunset one.
        self.interior_scene_lighting.reset(hdri_skybox="kiara_1_dawn_4k")
        # Load the scene, populate with objects.
        self.communicate(self.init_commands)
        # Start by the table. The teleport will occur on the next communicate() call.
        self.vr.set_position({"x": 0.7, "y": 0.0, "z": 1.0})
        while not self.vr.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = OculusLeapMotionInteriorScene()
    c.run()
