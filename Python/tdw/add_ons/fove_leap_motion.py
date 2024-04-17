from typing import List, Dict, Optional
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.leap_motion import LeapMotion
from tdw.output_data import OutputData, Fove
from tdw.vr_data.rig_type import RigType
from tdw.vr_data.fove.eye import Eye
from tdw.vr_data.fove.eye_state import EyeState
from tdw.vr_data.fove.calibration_state import CalibrationState
from tdw.vr_data.fove.calibration_sphere import CalibrationSphere
from tdw.type_aliases import PATH
import time
import numpy as np


class FoveLeapMotion(LeapMotion):
    """
    Add a FOVE human VR rig to the scene that uses Leap Motion hand tracking.
    """

    _CALIBRATION_COLOR_NOT_COLLIDING: Dict[str, float] = {"r": 1, "g": 1, "b": 1, "a": 1}
    _CALIBRATION_SPHERE_DIAMETER: float = 0.025
    _CALIBRATION_SPHERE_RADIUS: float = _CALIBRATION_SPHERE_DIAMETER / 2.0

    def __init__(self, calibration_data_path: PATH, perform_calibration: bool = False,
                 allow_headset_movement: bool = False, show_hands: bool = True, set_graspable: bool = True,
                 output_data: bool = True, position: Dict[str, float] = None, rotation: float = 0,
                 attach_avatar: bool = False, avatar_camera_width: int = 512, headset_aspect_ratio: float = 0.9,
                 headset_resolution_scale: float = 1.0, non_graspable: List[int] = None, max_graspable_mass: float = 50,
                 min_mass: float = 1, discrete_collision_detection_mode: bool = True,
                 set_object_physic_materials: bool = True, object_static_friction: float = 1,
                 object_dynamic_friction: float = 1, object_bounciness: float = 0, time_step: float = 0.02,
                 quit_button: Optional[int] = 3):
        """
        :param calibration_data_path: Calibration data will be saved to this file. Do not include a file extension!
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
        """:field
        An enum state machine flag that is used to check whether the FOVE headset is calibrating.
        """
        self.calibration_state: CalibrationState = CalibrationState.calibrating
        # The IDs of the calibration spheres.
        self._calibration_spheres: List[CalibrationSphere] = [CalibrationSphere(position) for position in
                                                              np.array([[-0.125, 0.9, -0.3], [0, 0.8, -0.3],
                                                                        [0.125, 0.7, -0.3], [-0.125, 0.7, -0.3],
                                                                        [0.125, 0.9, -0.3], [-0.1075, 0.9, -0.35],
                                                                        [0, 0.8, -0.35], [0.1075, 0.7, -0.35],
                                                                        [-0.1075, 0.7, -0.35], [0.1075, 0.9, -0.35],
                                                                        [-0.1, 0.9, -0.4], [0, 0.8, -0.4],
                                                                        [0.1, 0.7, -0.4], [-0.1, 0.7, -0.4],
                                                                        [0.1, 0.9, -0.4]])]
        # The calibration data.
        self._sphere_calibration_data: np.ndarray = np.zeros(shape=(2, len(self._calibration_spheres), 3))
        self._calibration_data_path: str = TDWUtils.get_string_path(calibration_data_path)

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
                         {"$type": "set_physics_solver_iterations", 
                          "iterations": 15},
                         {"$type": "set_time_step", 
                          "time_step": 0.01},
                         {"$type": "send_fove",
                          "frequency": "always"},
                         {"$type": "start_fove_calibration",
                          "profile_name": "test"}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        is_calibrated = False
        for i in range(len(resp) - 1):
            # Update FOVE data.
            if OutputData.get_data_type_id(resp[i]) == "fove":
                fove = Fove(resp[i])
                self.left_eye = FoveLeapMotion._get_eye(0, fove)
                self.right_eye = FoveLeapMotion._get_eye(1, fove)
                self.converged_eyes = FoveLeapMotion._get_eye(2, fove, converged=True)
                self.combined_depth = fove.get_combined_depth()
                is_calibrated = fove.get_is_calibrated()
        # Run FOVE's built-in calibration.
        if self.calibration_state == CalibrationState.calibrating:
            if is_calibrated:
                # Initialize sphere calibration.
                self._initialize_sphere_calibration()
        # Evaluate sphere calibration.
        elif self.calibration_state == CalibrationState.calibrating_with_spheres:
            self._evaluate_sphere_calibration()
        # Run the simulation normally.
        else:
            super().on_send(resp=resp)

    def initialize_scene(self) -> None:
        """
        This must be called after sphere calibration and after scene initialization.
        """

        self.commands.append({"$type": "send_static_rigidbodies",
                              "frequency": "once"})

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
                   gaze_id=fove.get_object_id(index) if fove.get_object_hit(index) else None,
                   gaze_position=fove.get_hit_position(index) if fove.get_hit(index) else None)

    def _initialize_sphere_calibration(self) -> None:
        """
        Initialize the sphere calibration phase of FOVE calibration.
        """

        self.calibration_state = CalibrationState.calibrating_with_spheres
        # Add position markers at each position.
        self.commands.extend([{"$type": "add_position_marker",
                               "position": TDWUtils.array_to_vector3(sphere.position),
                               "color": FoveLeapMotion._CALIBRATION_COLOR_NOT_COLLIDING,
                               "scale": FoveLeapMotion._CALIBRATION_SPHERE_DIAMETER}
                              for sphere in self._calibration_spheres])

    def _evaluate_sphere_calibration(self) -> None:
        """
        Evaluate an ongoing sphere calibration.
        """

        # Iterate through the spheres.
        for i in range(len(self._calibration_spheres)):
            # Ignore spheres that are done.
            if self._calibration_spheres[i].done:
                continue
            colliding = False
            # Check if any of the right hand's bones are within the position marker's radius.
            for bone in self.right_hand_transforms:
                if (np.linalg.norm(self.right_hand_transforms[bone].position - self._calibration_spheres[i].position)
                        <= FoveLeapMotion._CALIBRATION_SPHERE_RADIUS):
                    colliding = True
                    # Start calibration.
                    if self._calibration_spheres[i].t0 is None:
                        # Set the start time.
                        self._calibration_spheres[i].t0 = time.time()
                        # Remove all existing position markers.
                        self.commands.append({"$type": "remove_position_markers"})
                        # Replace the position markers. Set this marker's color.
                        self.commands.extend([{"$type": "add_position_marker",
                                               "position": TDWUtils.array_to_vector3(sphere.position),
                                               "color": {"r": 0, "g": 0, "b": 1, "a": 1} if i == j else FoveLeapMotion._CALIBRATION_COLOR_NOT_COLLIDING,
                                               "scale": FoveLeapMotion._CALIBRATION_SPHERE_DIAMETER}
                                              for j, sphere in enumerate(self._calibration_spheres) if not sphere.done])
                    # Continue ongoing calibration.
                    elif time.time() - self._calibration_spheres[i].t0 >= 0.5:
                        # The sphere is done.
                        self._calibration_spheres[i].done = True
                        # Store the calibration data.
                        self._sphere_calibration_data[0][i] = self.converged_eyes.gaze_position
                        self._sphere_calibration_data[1][i] = self.right_hand_transforms[bone].position
                        # Hide the sphere.
                        self._reset_sphere_colors()
                    # We only need to check one bone.
                    break
            # The user exited a collision before calibration was done.
            if not colliding and self._calibration_spheres[i].t0 is not None:
                self._calibration_spheres[i].t0 = None
                self._reset_sphere_colors()
        # Check whether the entire calibration is done.
        if all([sphere.done for sphere in self._calibration_spheres]):
            # Set the state to `running`.
            self.calibration_state = CalibrationState.running
            # Save the data to disk.
            np.save(self._calibration_data_path, self._sphere_calibration_data)
            # Destroy the spheres.
            self.commands.append({"$type": "remove_position_markers"})

    def _reset_sphere_colors(self) -> None:
        """
        Destroy all position markers and set their colors to the non-colliding color.
        """

        # Remove all existing position markers.
        self.commands.append({"$type": "remove_position_markers"})
        # Replace the position markers.
        self.commands.extend([{"$type": "add_position_marker",
                               "position": TDWUtils.array_to_vector3(sphere.position),
                               "color": FoveLeapMotion._CALIBRATION_COLOR_NOT_COLLIDING,
                               "scale": FoveLeapMotion._CALIBRATION_SPHERE_DIAMETER}
                              for j, sphere in enumerate(self._calibration_spheres) if not sphere.done])
