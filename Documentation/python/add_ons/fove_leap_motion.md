# FoveLeapMotion

`from tdw.add_ons.fove_leap_motion import FoveLeapMotion`

Add a FOVE human VR rig to the scene that uses Leap Motion hand tracking.

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `AVATAR_ID` | str | If an avatar is attached to the VR rig, this is the ID of the VR rig's avatar. | `"vr"` |
| `BONES` | List[FingerBone] | The finger bones as [`FingerBone`](../vr_data/finger_bone.md) values in the order that they'll appear in this add-on's dictionaries. | `[__b for __b in FingerBone]` |
| `NUM_DOFS` | Dict[FingerBone, int] | A dictionary. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = The number degrees of freedom for that bone. | `{__f: 3 if __f.name[-1] == "0" else 1 for __f in FingerBone if __f != FingerBone.palm}` |

***

## Fields

- `left_eye` The state, direction, and gaze object of the left eye.

- `right_eye` The state, direction, and gaze object of the right eye.

- `converged_eyes` The state, direction, and gaze object of the converged eyes.

- `combined_depth` The combined eye depth.

- `eye_hand_array` The numpy array used to store the eye/hand data.

- `calibration_state` An enum state machine flag that is used to check whether the FOVE headset is calibrating.

- `left_hand_transforms` A dictionary of [`Transform`](../object_data/transform.md) for each bone in the left hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = [`Transform`](../object_data/transform.md).

- `right_hand_transforms` A dictionary of [`Transform`](../object_data/transform.md) for each bone on the right hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = [`Transform`](../object_data/transform.md).

- `left_hand_collisions` A dictionary of object IDs for each bone on the left hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A list of IDs of objects that the bone is colliding with.

- `right_hand_collisions` A dictionary of object IDs for each bone in the right hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A list of IDs of objects that the bone is colliding with.

- `left_hand_angles` A dictionary of angles per finger bone on the left hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A numpy array of angles in degrees. Some bones have 3 angles and some have 1. See: `LeapMotion.NUM_DOFS`. The palm isn't in this dictionary.

- `right_hand_angles` A dictionary of angles per finger bone on the right hand. Key = [`FingerBone`](../vr_data/finger_bone.md). Value = A numpy array of angles in degrees. Some bones have 3 angles and some have 1. See: `LeapMotion.NUM_DOFS`. The palm isn't in this dictionary.

- `done` If True, the rig and the simulation are done. This can be useful to break a while loop in a controller. Pressing the quit button (see `quit_button`) will set this to True.

- `rig` The [`Transform`](../object_data/transform.md) data of the root rig object. If `output_data == False`, this is never updated.

- `left_hand` The [`Transform`](../object_data/transform.md) data of the left hand. If `output_data == False`, this is never updated.

- `right_hand` The [`Transform`](../object_data/transform.md) data of the right hand. If `output_data == False`, this is never updated.

- `head` The [`Transform`](../object_data/transform.md) data of the head. If `output_data == False`, this is never updated.

- `held_left` A numpy of object IDs held by the left hand.

- `held_right` A numpy of object IDs held by the right hand.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`FoveFoveLeapMotion(calibration_data_path)`**

**`FoveFoveLeapMotion(calibration_data_path, calibration_hand=Arm.right, timestamp=False, perform_calibration=False, restart_calibration=False, eye_by_eye_calibration=EyeByEyeCalibration.disabled, calibration_method=CalibrationMethod.spiral, eye_torsion_calibration=EyeTorsionCalibration.default, allow_headset_movement=False, allow_headset_rotation=True, show_hands=True, set_graspable=True, output_data=True, position=None, rotation=True, attach_avatar=False, avatar_camera_width=512, headset_aspect_ratio=0.9, headset_resolution_scale=1.0, non_graspable=None, max_graspable_mass=50, min_mass=1, discrete_collision_detection_mode=True, set_object_physic_materials=True, object_static_friction=1, object_dynamic_friction=1, object_bounciness=0, time_step=0.02, quit_button=3)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| calibration_data_path |  PATH |  | Calibration data will be saved to this file. Do not include a file extension! |
| calibration_hand |  Arm  | Arm.right | The hand used for sphere calibration. |
| timestamp |  bool  | False | Whether to append a time.time() timestamp to the calibration_data_path |
| perform_calibration |  bool  | False | If True, perform the calibration protocol. |
| restart_calibration |  bool  | False | If True, restart an ongoing calibration. |
| eye_by_eye_calibration |  EyeByEyeCalibration  | EyeByEyeCalibration.disabled | Indicate whether each eye should be calibrated separately or not. |
| calibration_method |  CalibrationMethod  | CalibrationMethod.spiral | Indicate the calibration method to use. |
| eye_torsion_calibration |  EyeTorsionCalibration  | EyeTorsionCalibration.default | Indicate whether each eye torsion calibration should be run. |
| allow_headset_movement |  bool  | False | If True, allow headset movement. |
| allow_headset_rotation |  bool  | True | If True, allow headset rotation. |
| show_hands |  bool  | True | If True, show the hands. |
| set_graspable |  bool  | True | If True, enabled "physics helpers" for all [non-kinematic objects](../../lessons/physx/physics_objects.md) that aren't listed in `non_graspable`. It's essentially not possible to grasp an object that doesn't have physics helpers. |
| output_data |  bool  | True | If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame. |
| position |  Dict[str, float] | None | The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}` |
| rotation |  bool  | True | The initial rotation of the VR rig in degrees. |
| attach_avatar |  bool  | False | If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`. |
| avatar_camera_width |  int  | 512 | The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow. |
| headset_aspect_ratio |  float  | 0.9 | The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices. |
| headset_resolution_scale |  float  | 1.0 | The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75 |
| non_graspable |  List[int] | None | A list of IDs of non-graspable objects, meaning that they don't have physics helpers (see `set_graspable`). By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable. |
| max_graspable_mass |  float  | 50 | Any objects with mass greater than or equal to this value won't have physics helpers. This will prevent the hands from attempting to grasp furniture. |
| min_mass |  float  | 1 | Unlike `max_graspable_mass`, this will actually set the mass of objects. Any object with a mass less than this value will be set to this value. |
| discrete_collision_detection_mode |  bool  | True | If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW). |
| set_object_physic_materials |  bool  | True | If True, set the physic material of each non-kinematic graspable object (see: `non_graspable`). |
| object_static_friction |  float  | 1 | If `set_object_physic_materials == True`, all non-kinematic graspable object will have this static friction value. |
| object_dynamic_friction |  float  | 1 | If `set_object_physic_materials == True`, all non-kinematic graspable object will have this dynamic friction value. |
| object_bounciness |  float  | 0 | If `set_object_physic_materials == True`, all non-kinematic graspable object will have this bounciness value. |
| time_step |  float  | 0.02 | The physics time step. Leap Motion tends to work better at this value. The TDW default is 0.01. |
| quit_button |  Optional[int] | 3 | The button used to quit the program as an integer: 0, 1, 2, or 3. If None, no quit button will be assigned. |

#### listen_to_button

**`self.listen_to_button(button, callback)`**

Listen for when a button is pressed.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| button |  int |  | The button as an integer: 0, 1, 2, or 3. |
| callback |  Callable[[] |  | A callback function to invoke when the button is pressed. The function must have no arguments and no return value. |

#### reset

**`self.reset()`**

**`self.reset(non_graspable=None, position=None, rotation=0)`**

Reset the VR rig. Call this whenever a scene is reset.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| non_graspable |  List[int] | None | A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable. |
| position |  Dict[str, float] | None | The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}` |
| rotation |  float  | 0 | The initial rotation of the VR rig in degrees. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### set_position

**`self.set_position(position)`**

Set the position of the VR rig.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] |  | The new position. |

#### rotate_by

**`self.rotate_by(angle)`**

Rotate the VR rig by an angle.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| angle |  float |  | The angle in degrees. |

#### show_loading_screen

**`self.show_loading_screen(show)`**

Show or hide the VR loading screen. To use this correctly, call this function followed by `c.communicate(commands)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| show |  bool |  | If True, show the loading screen. If False, hide the loading screen. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### initialize_scene

**`self.initialize_scene()`**

This must be called after sphere calibration and after scene initialization.

#### tilt_headset_by

**`self.tilt_headset_by(angle)`**

Tilt the headset in the scene by an angle.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| angle |  float |  | The angle in degrees. |