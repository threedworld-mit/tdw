from tdw.add_ons.oculus_touch import OculusTouch
from tdw.vr_data.oculus_touch_button import OculusTouchButton
from tdw.controller import Controller


class LoadingScreen(Controller):
    """
    A minimal example of how to use a VR loading screen.
    """

    SCENE_NAMES = ['mm_craftroom_2a', 'mm_craftroom_2b', 'mm_craftroom_3a', 'mm_craftroom_3b',
                   'mm_kitchen_2a', 'mm_kitchen_2b', 'mm_kitchen_3a', 'mm_kitchen_3b']

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.scene_index: int = 0
        # Add a VR rig.
        self.vr: OculusTouch = OculusTouch()
        self.done: bool = False
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        # Go to the next scene when the right trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=False, function=self.next_trial)
        self.add_ons.append(self.vr)
        # Load the first scene.
        self.next_trial()

    def run(self) -> None:
        # Loop until the user quits.
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self) -> None:
        self.done = True

    def next_trial(self) -> None:
        # Enable the loading screen.
        self.vr.show_loading_screen(show=True)
        self.communicate([])
        # Reset the VR rig.
        self.vr.reset()
        # Load the next scene.
        self.communicate([Controller.get_add_scene(scene_name=LoadingScreen.SCENE_NAMES[self.scene_index]),
                          Controller.get_add_object(model_name="rh10",
                                                    object_id=Controller.get_unique_id(),
                                                    position={"x": 0, "y": 0, "z": 0.5})])
        # Hide the loading screen.
        self.vr.show_loading_screen(show=False)
        self.communicate([])
        # Increment the scene index for the next scene.
        self.scene_index += 1
        if self.scene_index >= len(LoadingScreen.SCENE_NAMES):
            self.scene_index = 0


if __name__ == "__main__":
    c = LoadingScreen()
    c.run()
