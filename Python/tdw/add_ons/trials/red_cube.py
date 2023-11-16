from typing import List
from tdw.webgl.webgl_controller import WebGLController
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.mouse import Mouse
from tdw.add_ons.trials.trial import Trial
from tdw.add_ons.trials.trial_status import TrialStatus


class RedCube(Trial):
    """
    Click the red cube.
    """

    TARGET_OBJECT_ID: int = 1

    def __init__(self):
        # Set `self._mouse` here because we will need to refer to it on update.
        # This is needs to be BEFORE super().__init__() otherwise it won't exist when `self._get_add_ons()` is called.
        self._mouse: Mouse = Mouse()
        super().__init__()

    def _get_add_ons(self) -> List[AddOn]:
        return [self._mouse]

    def _get_trial_initialization_commands(self) -> List[dict]:
        # Add the scene.
        commands = WebGLController.get_add_scene(scene_name="box_room_2018")
        # Create the avatar (camera).
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 0.29, "z": -2.13}))
        # Add the cubes.
        s = 0.3
        for x, object_id, color in zip([-0.7, 0.7],
                                       [RedCube.TARGET_OBJECT_ID, RedCube.TARGET_OBJECT_ID + 1],
                                       [{"r": 1, "g": 0, "b": 0, "a": 1}, {"r": 0, "g": 0, "b": 1, "a": 1}]):
            commands.extend(WebGLController.get_add_physics_object(model_name="cube",
                                                                   library="models_flex.json",
                                                                   object_id=object_id,
                                                                   position={"x": x, "y": 0, "z": 0},
                                                                   scale_factor={"x": s, "y": s, "z": s},
                                                                   kinematic=True))
            commands.append({"$type": "set_color",
                             "id": object_id,
                             "color": color})
        return commands

    def _update_trial(self, resp: List[bytes]) -> None:
        # The mouse clicked an object.
        if self._mouse.left_button_pressed and self._mouse.mouse_is_over_object:
            if self._mouse.mouse_over_object_id == RedCube.TARGET_OBJECT_ID:
                self.status = TrialStatus.success
            else:
                self.status = TrialStatus.failure

    def _get_instructions(self) -> str:
        return "Click the <color=red>red</color> cube"

    def _get_trial_status(self, resp: List[bytes]) -> TrialStatus:
        # This function is useful if other add-ons such as a timer could affect the status.
        # In this example, the trial status is set in `self._update_trial()`.
        return self.status
