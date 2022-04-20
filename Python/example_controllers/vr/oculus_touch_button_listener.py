import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.vr_data.oculus_touch_button import OculusTouchButton


class OculusTouchButtonListener(Controller):
    """
    Listen for button presses to reset the scene.
    """

    MODEL_NAMES = ["rh10", "iron_box", "trunck"]

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.simulation_done = False
        self.trial_done = False
        self.vr = OculusTouch()
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        # End the trial when the right trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=False, function=self.end_trial)
        self.add_ons.extend([self.vr])
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def trial(self) -> None:
        self.vr.reset()
        # Start a new trial.
        self.trial_done = False
        # Choose a random model.
        model_name = random.choice(OculusTouchButtonListener.MODEL_NAMES)
        # Add the model.
        object_id = self.get_unique_id()
        self.communicate(self.get_add_object(model_name=model_name,
                                             object_id=object_id,
                                             position={"x": 0, "y": 0, "z": 1.2}))
        # Wait until the trial is done.
        while not self.trial_done and not self.simulation_done:
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})

    def run(self) -> None:
        while not self.simulation_done:
            # Run a trial.
            self.trial()
        # End the simulation.
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.simulation_done = True

    def end_trial(self):
        self.trial_done = True


if __name__ == "__main__":
    c = OculusTouchButtonListener()
    c.run()
