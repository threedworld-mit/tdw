from typing import List, Callable, Dict
import numpy as np
from tdw.add_ons.autohand import Autohand
from tdw.vr_data.rig_type import RigType
from tdw.vr_data.vive_eye_data import ViveEyeData, get_default_data
from tdw.vr_data.vive_button import ViveButton
from tdw.output_data import OutputData
from tdw.output_data import ViveProEye as _ViveProEyeOutputData


class ViveProEye(Autohand):
    """
    Add a VR rig to the scene that uses the Vive Pro Eye headset and controllers.

    Make all non-kinematic objects graspable by the rig.

    Per-frame, update the positions of the VR rig, its hands, and its head, as well as which objects it is grasping and the controller button presses.
    """

    def __init__(self, human_hands: bool = True, set_graspable: bool = True, output_data: bool = True,
                 position: Dict[str, float] = None, rotation: float = 0, attach_avatar: bool = False,
                 avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None,
                 discrete_collision_detection_mode: bool = True, gaze_radius: float = 0.1):
        """
        :param human_hands: If True, visualize the hands as human hands. If False, visualize the hands as robot hands.
        :param set_graspable: If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/composite_objects/overview.md) as graspable by the VR rig.
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all VR devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        :param non_graspable: A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param discrete_collision_detection_mode: If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW).
        :param gaze_radius: The radius of the spherecast used to find objects in the gaze focus.
        """

        super().__init__(human_hands=human_hands, set_graspable=set_graspable, output_data=output_data,
                         position=position, rotation=rotation, attach_avatar=attach_avatar,
                         avatar_camera_width=avatar_camera_width, headset_aspect_ratio=headset_aspect_ratio,
                         headset_resolution_scale=headset_resolution_scale, non_graspable=non_graspable,
                         discrete_collision_detection_mode=discrete_collision_detection_mode)
        # Button events.
        self._button_events: Dict[ViveButton, Callable[[], None]] = dict()
        """:field
        Eye tracking data in world space.
        """
        self.world_eye_data: ViveEyeData = get_default_data()
        """:field
        Eye tracking data relative to the head.
        """
        self.local_eye_data: ViveEyeData = get_default_data()
        """:field
        A list of object IDs in view of the headset.
        """
        self.focused_objects: List[int] = list()
        self._gaze_radius: float = gaze_radius

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.extend([{"$type": "set_vive_pro_eye_gaze_radius",
                          "gaze_radius": self._gaze_radius},
                         {"$type": "send_vive_pro_eye",
                         "frequency": "always"}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "vipe":
                vive_pro: _ViveProEyeOutputData = _ViveProEyeOutputData(resp[i])
                # Get the focused objects.
                self.focused_objects.clear()
                self.focused_objects.extend(vive_pro.get_focused())
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
                for j, clicked in enumerate(vive_pro.get_buttons()):
                    if clicked:
                        button = ViveButton(j)
                        if button in self._button_events:
                            self._button_events[button]()
                # Invoke axis events.
                for delta, axis in zip([vive_pro.get_left_axis(), vive_pro.get_right_axis()],
                                       [self._axis_events_left, self._axis_events_right]):
                    for event in axis:
                        event(delta)
                break

    def listen_to_button(self, button: ViveButton, function: Callable[[], None]) -> None:
        """
        Listen for Vive Pro controller button presses. For now, only buttons on the left controller are supported.

        :param button: The [`ViveButton`](../vr_data/vive_button.md) on the left controller.
        :param function: The function to invoke when the button is pressed. This function must have no arguments and return None.
        """

        self._button_events[button] = function

    def _get_human_hands(self) -> RigType:
        return RigType.vive_pro_eye_human_hands

    def _get_robot_hands(self) -> RigType:
        return RigType.vive_pro_eye_robot_hands
