# OculusTouch

`from tdw.add_ons.oculus_touch import OculusTouch`

Add a VR rig to the scene that uses Oculus Touch controllers.

Make all non-kinematic objects graspable by the rig.

Per-frame, update the positions of the VR rig, its hands, and its head, as well as which objects it is grasping and the controller button presses.

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `AVATAR_ID` | str | If an avatar is attached to the VR rig, this is the ID of the VR rig's avatar. | `"vr"` |

***

## Fields

- `vr_node_ids` Object IDs of the VR nodes (the body and hands).

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

**`OculusTouch()`**

**`OculusTouch(human_hands=True, set_graspable=True, output_data=True, position=None, rotation=0, attach_avatar=False, avatar_camera_width=512, headset_aspect_ratio=0.9, headset_resolution_scale=1.0, non_graspable=None, discrete_collision_detection_mode=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| human_hands |  bool  | True | If True, visualize the hands as human hands. If False, visualize the hands as robot hands. |
| set_graspable |  bool  | True | If True, set all [non-kinematic objects](../../lessons/physx/physics_objects.md) and [composite sub-objects](../../lessons/semantic_states/composite_objects.md) as graspable by the VR rig. |
| output_data |  bool  | True | If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame. |
| position |  Dict[str, float] | None | The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}` |
| rotation |  float  | 0 | The initial rotation of the VR rig in degrees. |
| attach_avatar |  bool  | False | If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`. |
| avatar_camera_width |  int  | 512 | The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow. |
| headset_aspect_ratio |  float  | 0.9 | The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices. |
| headset_resolution_scale |  float  | 1.0 | The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75 |
| non_graspable |  List[int] | None | A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable. |
| discrete_collision_detection_mode |  bool  | True | If True, the VR rig's hands and all graspable objects in the scene will be set to the `"discrete"` collision detection mode, which seems to reduce physics glitches in VR. If False, the VR rig's hands and all graspable objects will be set to the `"continuous_dynamic"` collision detection mode (the default in TDW). |

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

#### reset

**`self.reset()`**

**`self.reset(non_graspable=None, position=None, rotation=0)`**

Reset the VR rig. Call this whenever a scene is reset.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| non_graspable |  List[int] | None | A list of IDs of non-graspable objects. By default, all non-kinematic objects are graspable and all kinematic objects are non-graspable. Set this to make non-kinematic objects non-graspable. |
| position |  Dict[str, float] | None | The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}` |
| rotation |  float  | 0 | The initial rotation of the VR rig in degrees. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### listen_to_button

**`self.listen_to_button(button, is_left, function)`**

Listen for Oculus Touch controller button presses.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| button |  OculusTouchButton |  | The Oculus Touch controller button. |
| is_left |  bool |  | If True, this is the left controller. If False, this is the right controller. |
| function |  Callable[[] |  | The function to invoke when the button is pressed. This function must have no arguments and return None. |

#### listen_to_axis

**`self.listen_to_axis(is_left, function)`**

Listen for Oculus Touch controller axis events.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| is_left |  bool |  | If True, this is the left controller. If False, this is the right controller. |
| function |  Callable[[np.array] |  | The function to invoke when the button is pressed. This function must a single argument (a numpy array of shape `(2)`, representing (x, y) coordinates) and return None. |