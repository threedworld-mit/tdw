# VR

`from tdw.add_ons.vr import VR`

Add a VR rig to the scene.

Per-frame, update the positions of the VR rig, its hands, and its head, as well as which objects it is grasping.

Note that this is an abstract class. Different types of VR rigs use different subclasses of this add-on. See: [`OculusTouch`](oculus_touch.md).

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `AVATAR_ID` | str | If an avatar is attached to the VR rig, this is the ID of the VR rig's avatar. | `"vr"` |

***

## Fields

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

**`VR(rig_type)`**

**`VR(rig_type, output_data=True, position=None, rotation=0, attach_avatar=False, avatar_camera_width=512, headset_aspect_ratio=0.9, headset_resolution_scale=1.0)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| rig_type |  RigType |  | The [`RigType`](../vr_data/rig_type.md). |
| output_data |  bool  | True | If True, send [`VRRig` output data](../../api/output_data.md#VRRig) per-frame. |
| position |  Dict[str, float] | None | The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}` |
| rotation |  float  | 0 | The initial rotation of the VR rig in degrees. |
| attach_avatar |  bool  | False | If True, attach an [avatar](../../lessons/core_concepts/avatars.md) to the VR rig's head. Do this only if you intend to enable [image capture](../../lessons/core_concepts/images.md). The avatar's ID is `"vr"`. |
| avatar_camera_width |  int  | 512 | The width of the avatar's camera in pixels. *This is not the same as the VR headset's screen resolution!* This only affects the avatar that is created if `attach_avatar` is `True`. Generally, you will want this to lower than the headset's actual pixel width, otherwise the framerate will be too slow. |
| headset_aspect_ratio |  float  | 0.9 | The `width / height` aspect ratio of the VR headset. This is only relevant if `attach_avatar` is `True` because it is used to set the height of the output images. The default value is the correct value for all Oculus devices. |
| headset_resolution_scale |  float  | 1.0 | The headset resolution scale controls the actual size of eye textures as a multiplier of the device's default resolution. A value greater than 1 improves image quality but at a slight performance cost. Range: 0.5 to 1.75 |

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

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

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

**`self.reset(position=None, rotation=0)`**

Reset the VR rig. Call this whenever a scene is reset.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  Dict[str, float] | None | The initial position of the VR rig. If None, defaults to `{"x": 0, "y": 0, "z": 0}` |
| rotation |  float  | 0 | The initial rotation of the VR rig in degrees. |