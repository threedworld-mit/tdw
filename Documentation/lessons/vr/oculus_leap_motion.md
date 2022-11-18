##### Virtual Reality (VR)

# Oculus Leap Motion

The **Oculus Leap Motion** is a VR rig that uses an Oculus headset and [Leap Motion hand tracking](https://www.ultraleap.com/).

## Requirements

- Windows 10
- [A compatible GPU](https://support.oculus.com/articles/headsets-and-accessories/oculus-link/oculus-link-compatibility/)
- Oculus headset (Rift, Rift S, Quest, or Quest 2)
- *Quest and Quest 2:* An Oculus Link Cable
  - A USB-C port
- [The Oculus PC app](https://www.oculus.com/setup/)
- UltraLeap device
- [UltraLeap Gemini Tracking Software](https://developer.leapmotion.com/tracking-software-download) After installing Gemini Tracking software, you can open a useful control panel from the system tray that will show you the Leap camera view. You may need to set a couple of things in that control panel, the first time you use the hand tracking.
- You may need Touch controllers to navigate through the Oculus menus.

## Setup

- After installing the Oculus PC app, you must run it while running the controller and the build. 
- After installing Gemini Tracking software, you must run it while running the controller and the build.

## Rig description

**TODO**

## The `OculusLeapMotion` add-on

The simplest way to add an Oculus Touch rig to the scene is to use the [`OculusLeapMotion` add-on](../../python/add_ons/oculus_leap_motion.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
```

Result:

**TODO**

### Set the initial position and rotation

Set the initial position and rotation of the VR rig by setting `position` and `rotation` in the constructor or in `vr.reset()`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion(position={"x": 1, "y": 0, "z": 0}, rotation=30)
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
```

### Teleport and rotate the VR rig

**TODO**

### Hand poses

**TODO**

### Graspable objects

**TODO**

### Non-graspable

If you want certain non-kinematic objects to be non-graspable you can set the optional `non_graspable` parameter in the constructor:

```python
TODO
```

### Output data

- The `OculusLeapMotion` add-on saves the head, rig base, and hands data per-frame as [`Transform` objects](../../python/object_data/transform.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate([])
    print(vr.rig.position)
    print(vr.head.position)
    print(vr.left_hand.position)
    print(vr.right_hand.position)
    print("")
```

- The transforms of every finger bone are saved in `vr.left_hand_transforms` and `vr.right_hand_transforms`. These are dictionaries where the key is a [`Finger`](../../python/vr_data/finger.md) value and the value is another dictionary: The key is a [`FingerBone`](../../python/vr_data/finger_bone.md) value and the value is a [`Transform`](../../python/object_data/transform.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate([])
    for finger in vr.left_hand_transforms:
        for bone in vr.left_hand_transforms[finger]:
            position = vr.left_hand_transforms[finger][bone]
            print(finger, bone, position)
    print("")
```

- `vr.held_left` and `vr.held_right` are arrays of IDs of objects held in the left and right hands.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate([])
    print(vr.held_left, vr.held_right)
    print("")
```

- Per-finger bone collision data is stored in `vr.left_hand_collisions` and `vr.right_hand_collisions`. These are dictionaries where the key is a [`Finger`](../../python/vr_data/finger.md) value and the value is another dictionary: The key is a [`FingerBone`](../../python/vr_data/finger_bone.md) value and the value is a list of IDs of objects that are in contact with the finger bone (in other words, in either an `enter` or `stay` state):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
    for finger in vr.left_hand_collisions:
        for b in vr.left_hand_collisions[f]:
            if len(vr.left_hand_collisions[f][b]) > 0:
                print(f, b, vr.left_hand_collisions[f][b])
```

- Collision data for each palm is stored in `vr.left_palm_collisions` and `vr.right_palm_collisions`. These are lists of IDs of objects s that are in contact with the finger bone (in other words, in either an `enter` or `stay` state):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate([])
    if len(vr.left_palm_collisions) > 0:
        print(vr.left_palm_collisions)
```

You can disable output data by setting `output_data=False` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion(output_data=False)
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate([])
```

### Image capture

VR rig cameras are not [avatars](../core_concepts/avatars.md).  You can attach an avatar to a VR rig by setting `attach_avatar=True` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion(attach_avatar=True)
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while True:
    c.communicate([])
```

You can then adjust the camera and capture image data like with any other avatar. The ID of this avatar is always `"vr"`.

For performance reasons, the default width of the avatar's images is 512, which is lower than the resolution of the headset. The height is always scaled proportional to the width. To adjust the pixel width and height ratio, set `avatar_camera_width` and `headset_aspect_ratio` in the constructor.

### Loading screen

If you load a new scene, the VR rig will appear to act strangely while the scene is loading. This is harmless but can be unintuitive for new users.

You can "solve" this by adding a loading screen to the VR rig. Call `vr.show_loading_screen(True)` followed by `c.communicate([])` to show the loading screen. The `communicate([])` call should be sent *before* loading the scene. After loading the scene, call `vr.show_loading_screen(False)` followed by `c.communicate([])`

This is a minimal example of how to show and hide a loading screen (see `def next_trial(self):` for the loading screen code):

```python
TODO
```

### Reset

Whenever you reset a scene, you must call `vr.reset()` to re-initialize the VR add-on:

```python
TODO
```

If you want to reset a scene with an explicitly-defined non-graspable object, you must set the `non_graspable` parameter in both the constructor and in `reset()`:

```python
TODO
```

You can set an initial position and rotation with the optional `position` and `rotation` parameters:

```python
TODO
```

## Audio

*For more information regarding audio in TDW, [read this](../audio/overview.md).*

Audio is supported in the Oculus Leap Motion rig. Unlike other audio setups in TDW, it isn't necessary to [initialize audio](../audio/initialize_audio.md); the VR rig is already set up to listen for audio.

[Resonance Audio](../audio/resonance_audio.md) is *not* supported on the Oculus Leap Motion rig. Oculus does have audio spatialization but this hasn't yet been implemented in TDW.

This example controller adds an Oculus Leap Motion rig and [PyImpact](../audio/py_impact.md) to a scene:

```python
TODO
```

## Low-level commands

The `OculusLeapMotion` initializes the rig with the following commands:

- [`create_vr_rig`](../../api/command_api.md#create_vr_rig)
- [`set_vr_resolution_scale`](../../api/command_api.md#set_vr_resolution_scale)
- [`set_post_process`](../../api/command_api.md#set_post_process) (Disables post-process)
- [`send_vr_rig`](../../api/command_api.md#send_vr_rig) (Sends [`VRRig`](../../api/output_data.md#VRRig) output data every frame)
- [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig) (If `attach_avatar` in the constructor is True)
- [`set_screen_size`](../../api/command_api.md#set_screen_size) (If `attach_avatar` in the constructor is True; this sets the size of the images captured by the avatar)
- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies) (Only once, and only if `set_graspable` in the constructor is True. This will return [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies) output data, which is used to set graspable objects)
- [`send_leap_moption`](../../api/command_api.md#send_leap_moption)
-  [`send_static_oculus_touch`](../../api/command_api.md#send_static_oculus_touch) (Sends [`StaticOculusTouch`](../../api/output_data.md#StaticOculusTouch) output data on the first frame)

On the second `communicate()` call after initialization:

- Using `StaticRigidbodies` data, send [`set_vr_graspable`](../../api/command_api.md#set_vr_graspable) for each non-kinematic object in the scene.

Position and rotation:

- [`teleport_vr_rig`](../../api/command_api.md#teleport_vr_rig)
- [`rotate_vr_rig_by`](../../api/command_api.md#rotate_vr_rig_by)

Loading screen:

- [`set_vr_loading_screen`](../../api/command_api.md#set_vr_loading_screen)

On the backend, the root body and hands are cached as objects with their own IDs (generated randomly by the build).

***

[Return to the README](../../../README.md)

***

Python API:

- [`OculusTouch`](../../python/add_ons/oculus_touch.md)
- [`OculusTouchButton`](../../python/vr_data/oculus_touch_button.md)
- [`Transform`](../../python/object_data/transform.md)

Example controllers:

- [oculus_touch_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_minimal.py) Minimal VR example.
- [oculus_touch_button_listener.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_button_listener.py) Listen for button presses to reset the scene.
- [oculus_touch_composite_object.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_composite_object.py) Manipulate a composite object in VR.
- [oculus_touch_output_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_output_data.py) Add several objects to the scene and parse VR output data.
- [oculus_touch_image_capture.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_image_capture.py) Add several objects to the scene. Record which objects are visible to the VR agent.
- [oculus_touch_py_impact.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_py_impact.py) Listen to audio generated by PyImpact.
- [oculus_touch_axis_listener.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_axis_listener.py) Control a robot arm with the Oculus Touch control sticks.
- [oculus_touch_loading_screen.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_touch_loading_screen.py) A minimal example of how to use a VR loading screen.

Command API:

- [`create_vr_rig`](../../api/command_api.md#create_vr_rig)
- [`set_vr_resolution_scale`](../../api/command_api.md#set_vr_resolution_scale)
- [`set_post_process`](../../api/command_api.md#set_post_process)
- [`send_vr_rig`](../../api/command_api.md#send_vr_rig) 
- [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig)
- [`set_screen_size`](../../api/command_api.md#set_screen_size)
- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies)
- [`send_oculus_touch_buttons`](../../api/command_api.md#send_oculus_touch_buttons)
- [`set_vr_graspable`](../../api/command_api.md#set_vr_graspable)
- [`teleport_vr_rig`](../../api/command_api.md#teleport_vr_rig)
- [`rotate_vr_rig_by`](../../api/command_api.md#rotate_vr_rig_by)
- [`send_static_oculus_touch`](../../api/command_api.md#send_static_oculus_touch)
- [`set_vr_loading_screen`](../../api/command_api.md#set_vr_loading_screen)

Output Data:

- [`VRRig`](../../api/output_data.md#VRRig)
- [`OculusTouchButtons`](../../api/output_data.md#OculusTouchButtons)
- [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies)
- [`StaticOculusTouch`](../../api/output_data.md#StaticOculusTouch)
