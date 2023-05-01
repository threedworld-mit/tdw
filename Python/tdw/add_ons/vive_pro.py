from typing import List, Callable, Dict
import numpy as np
from tdw.add_ons.autohand import Autohand
from tdw.vr_data.vive_eye_data import ViveEyeData, get_default_data
from tdw.vr_data.rig_type import RigType
from tdw.output_data import OutputData
from tdw.output_data import VivePro as Vive


class VivePro(Autohand):
    """
    Add a VR rig to the scene that uses the Vive Pro Eye headset and controllers.

    Make all non-kinematic objects graspable by the rig.

    Per-frame, update the positions of the VR rig, its hands, and its head, as well as which objects it is grasping and the controller button presses.
    """

    def __init__(self, human_hands: bool = True, set_graspable: bool = True, output_data: bool = True,
                 position: Dict[str, float] = None, rotation: float = 0, attach_avatar: bool = False,
                 avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None,
                 discrete_collision_detection_mode: bool = True):
        """
        :param human_hands: If True, visualize the hands as human hands. If False, visualize the hands as robot hands.
        :param set_graspable: If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/composite_objects/overview.md) as graspable by the VR rig.
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param discrete_collision_detection_mode: If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW).
        """

        super().__init__(human_hands=human_hands, set_graspable=set_graspable, output_data=output_data,
                         position=position, rotation=rotation, attach_avatar=attach_avatar,
                         avatar_camera_width=avatar_camera_width, headset_aspect_ratio=headset_aspect_ratio,
                         headset_resolution_scale=headset_resolution_scale, non_graspable=non_graspable,
                         discrete_collision_detection_mode=discrete_collision_detection_mode)
        # Button press events.
        self._button_press_events_left: Dict[int, Callable[[], None]] = dict()
        self._button_press_events_right: Dict[int, Callable[[], None]] = dict()
        """:field
        Eye tracking data in world space.
        """
        self.world_eye_data: ViveEyeData = get_default_data()
        """:field
        Eye tracking data relative to the head.
        """
        self.local_eye_data: ViveEyeData = get_default_data()

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.append({"$type": "send_vive_pro",
                         "frequency": "always"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "vivp":
                vive_pro: Vive = Vive(resp[i])
                # Get the world eye tracking data.
                blinking = vive_pro.get_blinking()
                self.world_eye_data.valid = vive_pro.get_valid(0)
                self.world_eye_data.ray = vive_pro.get_eye_ray(0)
                self.world_eye_data.blinking = blinking
                self.local_eye_data.valid = vive_pro.get_valid(1)
                self.local_eye_data.ray = vive_pro.get_eye_ray(1)
                self.local_eye_data.blinking = np.copy(blinking)
                # Get the axis data.
                for delta, axis in zip([vive_pro.get_left_axis(), vive_pro.get_right_axis()],
                                       [self._axis_events_left, self._axis_events_right]):
                    for event in axis:
                        event(delta)
                # Listen for button presses.
                for j, button in enumerate(vive_pro.get_left_buttons()):
                    if button and j in self._button_press_events_left:
                        self._button_press_events_left[j]()
                for j, button in enumerate(vive_pro.get_right_buttons()):
                    if button and j in self._button_press_events_right:
                        self._button_press_events_right[j]()
                break

    def listen_to_button(self, button: int, is_left: bool, function: Callable[[], None]) -> None:
        """
        Listen for Vive Pro controller button presses.

         TODO: This doesn't work! Buttons have to be mapped to enum values somehow. There needs to be a command to add them to the list of what we're listening for.

        :param button: The button index.
        :param is_left: If True, this is the left controller. If False, this is the right controller.
        :param function: The function to invoke when the button is pressed. This function must have no arguments and return None.
        """

        if is_left:
            self._button_press_events_left[button] = function
        else:
            self._button_press_events_right[button] = function

    def _get_human_hands(self) -> RigType:
        return RigType.vive_pro_human_hands

    def _get_robot_hands(self) -> RigType:
        return RigType.vive_pro_robot_hands
