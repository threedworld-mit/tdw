from typing import List, Dict, Optional
from tdw.add_ons.leap_motion import LeapMotion
from tdw.output_data import OutputData, Fove
from tdw.vr_data.rig_type import RigType
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState
from tdw.vr_data.fove.run_mode import RunMode


class FoveLeapMotion(LeapMotion):
    """
    Add a FOVE human VR rig to the scene that uses Leap Motion hand tracking.
    """

    def __init__(self, perform_calibration: bool = False, allow_headset_movement: bool = False, show_hands: bool = True, set_graspable: bool = True,
                 output_data: bool = True, position: Dict[str, float] = None, rotation: float = 0,
                 attach_avatar: bool = False, avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None, max_graspable_mass: float = 50,
                 min_mass: float = 1, discrete_collision_detection_mode: bool = True,
                 set_object_physic_materials: bool = True, object_static_friction: float = 1,
                 object_dynamic_friction: float = 1, object_bounciness: float = 0, time_step: float = 0.02,
                 quit_button: Optional[int] = 3):
        """
        :param perform_calibration: If True, perform the calibration protocol.
        :param allow_headset_movement: If True, allow headset movement.
        :param show_hands: If True, show the hands.
        :param set_graspable: If True, enabled "physics helpers" for all [non-kinematic objects](../../lessons/physx/physics_objects.md) that aren't listed in `non_graspable`. It's essentially not possible to grasp an object that doesn't have physics helpers.
        :param output_data: If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame.
        :param position: The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}`
        :param rotation: The initial rotation of the VR rig in degrees.
        :param attach_avatar: If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`.
        :param avatar_camera_width: The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow.
        :param headset_aspect_ratio: The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices.
        :param headset_resolution_scale: The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75
        :param non_graspable: A list of IDs of non-graspable objects, meaning that they don't have physics helpers (see `set_graspable`). By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable.
        :param max_graspable_mass: Any objects with mass greater than or equal to this value won't have physics helpers. This will prevent the hands from attempting to grasp furniture.
        :param min_mass: Unlike `max_graspable_mass`, this will actually set the mass of objects. Any object with a mass less than this value will be set to this value.
        :param discrete_collision_detection_mode: If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW).
        :param set_object_physic_materials: If True, set the physic material of each non-kinematic graspable object (see: `non_graspable`).
        :param object_static_friction: If `set_object_physic_materials == True`, all non-kinematic graspable object will have this static friction value.
        :param object_dynamic_friction: If `set_object_physic_materials == True`, all non-kinematic graspable object will have this dynamic friction value.
        :param object_bounciness: If `set_object_physic_materials == True`, all non-kinematic graspable object will have this bounciness value.
        :param time_step: The physics time step. Leap Motion tends to work better at this value. The TDW default is 0.01.
        :param quit_button: The button used to quit the program as an integer: 0, 1, 2, or 3. If None, no quit button will be assigned.
        """

        super().__init__(rig_type=RigType.fove_leap_motion,
                         output_data=output_data,
                         position=position,
                         rotation=rotation, attach_avatar=attach_avatar,
                         avatar_camera_width=avatar_camera_width,
                         headset_aspect_ratio=headset_aspect_ratio,
                         headset_resolution_scale=headset_resolution_scale,
                         set_graspable=set_graspable,
                         non_graspable=non_graspable,
                         max_graspable_mass=max_graspable_mass,
                         min_mass=min_mass,
                         discrete_collision_detection_mode=discrete_collision_detection_mode,
                         set_object_physic_materials=set_object_physic_materials,
                         object_static_friction=object_static_friction,
                         object_dynamic_friction=object_dynamic_friction,
                         object_bounciness=object_bounciness,
                         time_step=time_step, quit_button=quit_button)
        self._perform_calibration: bool = perform_calibration
        self._allow_headset_movement: bool = allow_headset_movement
        self._show_hands: bool = show_hands
        """:field
        The state, direction, and gaze object of the left eye.
        """
        self.left_eye: Optional[Eye] = None
        """:field
        The state, direction, and gaze object of the right eye.
        """
        self.right_eye: Optional[Eye] = None
        """:field
        The state, direction, and gaze object of the converged eyes.
        """
        self.converged_eyes: Optional[Eye] = None
        """:field
        The combined eye depth.
        """
        self.combined_depth: float = 0

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.extend([{"$type": "allow_fove_headset_movement",
                          "allow": self._allow_headset_movement},
                         {"$type": "show_leap_motion_hands",
                          "show": self._show_hands},
                         {"$type": "set_vsync_count",
                          "count": 0},
                         {"$type": "set_post_process",
                          "value": False},
                         {"$type": "set_target_framerate",
                          "framerate": -1},
                         {"$type": "send_fove",
                          "frequency": "always"}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            # Update FOVE data.
            if OutputData.get_data_type_id(resp[i]) == "fove":
                fove = Fove(resp[i])
                self.left_eye = FoveLeapMotion._get_eye(0, fove)
                self.right_eye = FoveLeapMotion._get_eye(1, fove)
                self.converged_eyes = FoveLeapMotion._get_eye(2, fove, converged=True)
                self.combined_depth = fove.get_combined_depth()

    @staticmethod
    def _get_eye(index: int, fove: Fove, converged: bool = False) -> Eye:
        """
        :param index: The index of the raw eye data.
        :param fove: `Fove` output data.
        :param converged: If True, this is the converged eyes.

        :return: `Eye` data.
        """

        return Eye(state=EyeState.converged if converged else fove.get_eye_state(index),
                   direction=fove.get_eye_direction(index),
                   gaze_id=fove.get_object_id(index) if fove.get_object_hit(index) else None)
