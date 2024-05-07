##### Virtual Reality (VR)

# FOVE Leap Motion

The **FOVELeap Motion** is a VR rig that uses an FOVE headset and [Leap Motion hand tracking](https://www.ultraleap.com/).

## Requirements

- Windows 10
- GPU
- FOVE headset
- FOVE runtime app. Installation is free but you must first fill out an [application form](https://fove-inc.com/fove-vr-platform-contact/). You will then receive an email with the license information and a link to the download. Install and launch the app. Paste the license into a pop-up window. Then click right on the FOVE tray at the bottom-right corner of the screen and click on "Activate".
- [Leap Motion Controller 2](https://www.adafruit.com/product/5758?gad_source=1&gclid=CjwKCAjwouexBhAuEiwAtW_Zx9KomkkHvehnqVFPDCMP_JWbjV90IfHUHmakS2DXqvsZ5Xn6cNMc-xoCr-QQAvD_BwE)
- [UltraLeap device mount](https://www.mouser.com/ProductDetail/Ultraleap/LM-VR?qs=wnTfsH77Xs4W1KBbR6YVHQ%3D%3D) 
- [UltraLeap Gemini Tracking Software](https://developer.leapmotion.com/tracking-software-download) After installing Gemini Tracking software, you can open a useful control panel from the system tray that will show you the Leap camera view. You may need to set a couple of things in that control panel, the first time you use the hand tracking.

## Setup

- Start the FOVE runtime app. When first launching the runtime, it will start automatically and the "switch" under the word "FOVE" will be green. For the headset to be fully recognized,  click the switch and then click it back on again.
- Start the UltraLeap Gemini tracking app, if it hasn't started automatically.

## Rig description

Like the [Oculus Leap Motion rig](oculus_leap_motion.md), the FOVE Leap Motion rig has two floating hands that track a human user's actual hands. The hands are physically embodied, meaning that they can interact with objects, either by pushing them or by picking them up and putting them down. The remainder of the user's body, such as arms and legs, are not rendered or physically embodied.

Unlike the [Oculus Touch](oculus_touch.md) rig, the FOVE Leap Motion rig cannot teleport. 

The FOVE Leap Motion rig receives rig, hand, and eye-tracking data per-frame.

## The `FoveLeapMotion` add-on

The simplest way to add an FOVE Leap Motion rig to the scene is to use the [`FoveLeapMotion`](../../python/add_ons/fove_leap_motion.md).

**There are many more constructor parameters not shown in this example. For the full API, [read this](../../python/add_ons/fove_leap_motion.md).**

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.fove_leap_motion import FoveLeapMotion
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.vr_data.fove.calibration_state import CalibrationState

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("fove_scene/calibration_data_")
print(f"Calibration data will be saved to: {path.parent}")
fove = FoveLeapMotion(position={"x": 0, "y": 1.0, "z": 0},
                      rotation=180.0,
                      attach_avatar=False,
                      time_step=0.01,
                      allow_headset_movement=False,
                      allow_headset_rotation=False,
                      calibration_data_path=str(path.resolve()),
                      timestamp=True)
c.add_ons.append(fove)
c.communicate(commands)

while not fove.done:
    # Test if calibration done.
    if fove.calibration_state == CalibrationState.running:
        fove.initialize_scene()
    c.communicate([])
   
c.communicate({"$type": "terminate"})
```

### Calibration

The FOVE Leap Motion rig must be calibrated every time it is used. There are two calibration steps that automatically occur prior to any scene.

1. The FOVE’s internal Spiral calibration protocol, in which the user follows with their eyes a green dot moving in a spiral.
2. A custom calibration that measures hand and eye tracking combined. The TDW scene reappears and a 5 x 3 grid of 3D spheres is positioned in front of the user’s view. The user must touch each of the spheres in turn; the spheres turn blue upon contact and remain blue as long as the touch is maintained. After 0.5 seconds of consistent touch, the sphere is considered calibrated and disappears. This result of this calibration step is dumped to disk as a numpy (.npy) file.

### Scene initialization

After calibration, your controller should send commands to initialize the actual scene. On the same frame that you add the scene and its objects, call `fove.initialize_scene()`. This will ensure that the rig has the data it needs to interact with objects.

### Headset tracking

For headset tracking, the FOVE uses a single IR sensor that is read by IR LEDs inside the headset. This sensor is small and can be mounted on any standard tripod or mounting system.

By default, the FOVE Leap Motion rig will *not* track the headset. To  enable positional tracking, set `allow_headset_movement=True` in the add-on's constructor. To enable rotational tracking, set `allow_headset_rotation=True` in the add-on's constructor.

To enable positional tracking, you must also run the FOVE Debug Tool. Click on the FOVE runtime tray and select "Launch Debug Tool". Once launched, a green light will appear on the position tracker.

### Tilt the headset

If rotational tracking is disabled, it still might be useful to tilt (pitch) the headset up or down in the scene. To do so, call `fove.tilt_headset_by(angle)`. `angle` is in degrees.

### UI Buttons

Unlike the [Oculus Leap Motion rig](oculus_leap_motion.md#ui-buttons), UI buttons are disabled in the FOVE Leap Motion rig.

### The `vr.done` field

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#the-vrdone-field).

### Set the initial position and rotation

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#set-the-initial-position-and-rotation).

### Graspable objects

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#graspable-objects).

### Object physics

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#object-physics).

### Output data

VR Rig data and Leap Motion hand data is the same as in [Oculus Leap Motion rig](oculus_leap_motion.md#output-data).

Additionally, the FOVE Leap Motion rig receives eye tracking data:

- `fove.right_eye`, `fove.left_eye`, and `fove.converged_eye` store [`Eye` data](../../python/vr_data/fove/eye.md), which includes the gaze direction, whether the eye is gazing at an object, and the [`EyeState`](../../python/vr_data/fove/eye_state.md). This is updated automatically per-frame.
- `fove.combined_depth` is the combined eye depth (a float value). This is updated automatically per-frame.
- `fove.calibration_state` describes the current [`CalibrationState`](../../python/vr_data/fove/calibration_state.md).
- `fove.eye_hand_array` is a numpy array of the sphere calibration data (see above).

For an example controller that uses eye tracking data, see: `tdw/Python/example_controllers/vr/fove_eye_tracking.py`.

### Image capture

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#image-capture).

### Loading screen

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#loading-screen).

### Reset

This works exactly the same as in the [Oculus Leap Motion rig](oculus_leap_motion.md#reset).

***

[Return to the README](../../../README.md)

***

Python API:

- [`FoveLeapMotion`](../../python/add_ons/fove_leap_motion.md)
- [`Eye`](../../python/vr_data/fove/eye.md)
- [`EyeState`](../../python/vr_data/fove/eye_state.md)
- [`CalibrationState`](../../python/vr_data/fove/calibration_state.md)

Example controllers:

- [fove_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/fove_minimal.py) Minimal FOVE VR example.
- [fove_eye_tracking.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/fove_eye_tracking.py) Use eye tracking data to reveal and highlight objects in the scene.

Command API:

- [`create_vr_rig`](../../api/command_api.md#create_vr_rig)
- [`set_vr_resolution_scale`](../../api/command_api.md#set_vr_resolution_scale)
- [`set_post_process`](../../api/command_api.md#set_post_process)
- [`send_vr_rig`](../../api/command_api.md#send_vr_rig) 
- [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig)
- [`set_screen_size`](../../api/command_api.md#set_screen_size)
- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies)
- [`ignore_leap_motion_physics_helpers`](../../api/command_api.md#ignore_leap_motion_physics_helpers)
- [`set_vr_loading_screen`](../../api/command_api.md#set_vr_loading_screen)
- [`set_time_step`](../../api/command_api.md#set_time_step)
- [`set_object_collision_detection_mode`](../../api/command_api.md#set_object_collision_detection_mode)
- [`set_physic_material`](../../api/command_api.md#set_physic_material)
- [`allow_fove_headset_movement`](../../api/command_api.md#allow_fove_headset_movement)
- [`allow_fove_headset_rotation`](../../api/command_api.md#allow_fove_headset_rotation)
- [`show_leap_motion_hands`](../../api/command_api.md#show_leap_motion_hands)
- [`set_vsync_count`](../../api/command_api.md#set_vsync_count)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)
- [`set_physics_solver_iterations`](../../api/command_api.md#set_physics_solver_iterations)
- [`send_fove`](../../api/command_api.md#send_fove)
- [`start_fove_calibration`](../../api/command_api.md#start_fove_calibration)
- [`refresh_leap_motion_rig`](../../api/command_api.md#refresh_leap_motion_rig)
- [`tilt_fove_rig_by`](../../api/command_api.md#tilt_fove_rig_by)

Output Data:

- [`VRRig`](../../api/output_data.md#VRRig)
- [`LeapMotion`](../../api/output_data.md#LeapMotion)
- [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies)
- [`Fove`](../../api/output_data.md#Fove)
