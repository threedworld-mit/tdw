##### Virtual Reality (VR)

# Oculus Leap Motion

The **Oculus Leap Motion** is a VR rig that uses an Oculus headset and [Leap Motion hand tracking](https://www.ultraleap.com/).

![](images/oculus_leap_motion/interior_scene.gif)

## Requirements

- Windows 10
- [A compatible GPU](https://support.oculus.com/articles/headsets-and-accessories/oculus-link/oculus-link-compatibility/)
- Oculus headset (Rift, Rift S, Quest, or Quest 2)
- *Quest and Quest 2:* An Oculus Link Cable
  - A USB-C port
- [The Oculus PC app](https://www.oculus.com/setup/)
- [UltraLeap device](https://www.adafruit.com/product/2106)
- [UltraLeap Gemini Tracking Software](https://developer.leapmotion.com/tracking-software-download) After installing Gemini Tracking software, you can open a useful control panel from the system tray that will show you the Leap camera view. You may need to set a couple of things in that control panel, the first time you use the hand tracking.
- You may need Touch controllers to navigate through the Oculus menus.

## Setup

- After installing the Oculus PC app, you must run it while running the controller and the build. 
- After installing Gemini Tracking software, you must run it while running the controller and the build.

## Rig description

The Oculus Leap Motion VR rig has two floating hands that track a human user's actual hands. The hands are visible and physically embodied, meaning that they can interact with objects, either by pushing them or by picking them up and putting them down. The remainder of the user's body, such as arms and legs, are not rendered or physically embodied.

Unlike the [Oculus Touch](oculus_touch.md) rig, the Oculus Leap Motion rig cannot teleport. We intend to add teleportation later.

## The `OculusLeapMotion` add-on

The simplest way to add an Oculus Touch rig to the scene is to use the [`OculusLeapMotion`](../../python/add_ons/oculus_leap_motion.md) add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
z = 0.6
commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 0, "z": z},
                                                  kinematic=True))
commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                  object_id=Controller.get_unique_id(),
                                                  position={"x": 0, "y": 1, "z": z - 0.25},
                                                  scale_mass=False,
                                                  scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                  default_physics_values=False,
                                                  mass=1,
                                                  library="models_flex.json"))
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(commands)
while not vr.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

### UI Buttons

**If the user positions their left palm in front of the camera, four UI buttons will appear.** 

These buttons can be mapped to Python functions via `vr.listen_to_button(button, callback)`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion


class OculusLeapMotionUI(Controller):
    """
    Press 0 to make the cube red. Press 4 to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vr = OculusLeapMotion()
        self.cube_id: int = Controller.get_unique_id()
        self.vr.listen_to_button(button=0, callback=self.set_cube_color)
        self.add_ons.extend([self.vr])

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        z = 0.6
        commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 0, "z": z},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=self.cube_id,
                                                          position={"x": 0, "y": 1, "z": z - 0.25},
                                                          scale_mass=False,
                                                          scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                          default_physics_values=False,
                                                          mass=1,
                                                          library="models_flex.json"))
        self.communicate(commands)
        while not self.vr.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def set_cube_color(self) -> None:
        self.communicate({"$type": "set_color",
                          "id": self.cube_id,
                          "color": {"r": 1, "g": 0, "b": 0, "a": 1}})


if __name__ == "__main__":
    c = OculusLeapMotionUI()
    c.run()
```

Result:

![](images/oculus_leap_motion/ui.gif)

### The `vr.done` field

In the previous example, as in others, the `while` loop is controlled by `vr.done`. 

**If you press button 3, the build will send output data that will set `vr.done` to True.** 

You can think of button 3 as a "quit button", but it doesn't actually quit the simulation or send any commands--by default, all it will do is set `vr.done` to True, which you can use to control the main loop.

You can set a different button via the optional `quit_button` parameter in the `OculusLeapMotion` constructor: `vr = OculusLeapMotion(quit_button=2)`. Or, you can set no button: `vr = OculusLeapMotion(quit_button=None)`.

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
while not vr.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

### Graspable objects

Grasping objects is achieved by applying "physics helper" scripts, without which it is difficult, if not impossible, to grasp objects; reasons for this vary but in general it's too difficult to wholly recreate the physics of a human hand gripping an object.

You can disable "physics helpers" by setting `set_graspable=False` in the `OculusLeapMotion` constructor.

There are built-in constraints to which objects receive "physics helpers", some of which can be adjusted:

- [Kinematic](../physx/physics_objects.md) objects never receive physics helpers.
- High-mass objects don't receive physics helpers. See the `max_graspable_mass` parameter in the in the `OculusLeapMotion` constructor.
- You can set certain objects to not receive "physics helpers" by setting the `non_graspable`  in the in the `OculusLeapMotion` constructor: `vr = OculusLeapMotion(non_graspable=[object_id_0, object_id_1])`.

### Object physics

The `OculusLeapMotion` add-on adjusts the physics properties of all objects about to receive "physics helpers" to prevent physics glitches:

- Each object with less mass than a given threshold has its mass set to that threshold. By default, the threshold is 1. To adjust the threshold, set the `min_mass` parameter in the `OculusLeapMotion` constructor.
- Each object's collision detection mode is set to "discrete" instead of the default "continuous dynamic". To disable this, set `discrete_collision_detection_mode=False`  in the `OculusLeapMotion` constructor.
- Each object's [physic material](../physx/physics_objects.md) is set to have the highest possible friction values and no bounciness. Adjust these global values via the `object_static_friction`, `object_dynamic_friction`, and `object_bounciness` parameters in the `OculusLeapMotion` constructor. To *not* set global physic material values, set `set_object_physic_materials=False`.
- The physics time step is set to 0.02 seconds instead of TDW's typical 0.01 seconds. To adjust this, set the `time_step` parameter in the `OculusLeapMotion` constructor.

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
while not vr.done:
    c.communicate([])
    print(vr.rig.position)
    print(vr.head.position)
    print(vr.left_hand.position)
    print(vr.right_hand.position)
    print("")
c.communicate({"$type": "terminate"})
```

- The transforms of every finger bone are saved in `vr.left_hand_transforms` and `vr.right_hand_transforms`. These are dictionaries where the key is a [`FingerBone`](../../python/vr_data/finger_bone.md) value and the value is a [`Transform`](../../python/object_data/transform.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion

c = Controller()
vr = OculusLeapMotion()
c.add_ons.append(vr)
c.communicate(TDWUtils.create_empty_room(12, 12))
while not vr.done:
    c.communicate([])
    for bone in vr.left_hand_transforms:
        position = vr.left_hand_transforms[bone]
        print(bone, position)
    print("")
c.communicate({"$type": "terminate"})
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
while not vr.done:
    c.communicate([])
    print(vr.held_left, vr.held_right)
    print("")
c.communicate({"$type": "terminate"})
```

- Per-finger bone collision data is stored in `vr.left_hand_collisions` and `vr.right_hand_collisions`. These are dictionaries where the key is a [`FingerBone`](../../python/vr_data/finger_bone.md) value and the value is a list of IDs of objects that are in contact with the finger bone (in other words, in either an `enter` or `stay` state):

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
while not vr.done:
    c.communicate([])
    for bone in vr.left_hand_collisions:
        if len(vr.left_hand_collisions[bone]) > 0:
            print(bone, vr.left_hand_collisions[bone])
c.communicate({"$type": "terminate"})
```

You can disable output data by setting `output_data=False` in the constructor. Be aware that this will also disable UI functionality.

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

VR rig cameras are not [avatars](../core_concepts/avatars.md).  You can attach an avatar to a VR rig by setting `attach_avatar=True` in the constructor and optionally include an [`ImageCapture`](../core_concepts/images.md) add-on. The ID of the VR rig's avatar is always `"vr"`.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("vr_images")
c = Controller()
vr = OculusLeapMotion(attach_avatar=True)
capture = ImageCapture(path=path, avatar_ids=["vr"])
c.add_ons.extend([vr, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
while not vr.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
```

From there, the camera and images can be adjusted as with any other avatar.

For performance reasons, the default width of the avatar's images is 512, which is lower than the resolution of the headset. The height is always scaled proportional to the width. To adjust the pixel width and height ratio, set `avatar_camera_width` and `headset_aspect_ratio` in the constructor.

### Loading screen

If you load a new scene, the VR rig will appear to act strangely while the scene is loading. This is harmless but can be unintuitive for new users.

You can "solve" this by adding a loading screen to the VR rig. Call `vr.show_loading_screen(True)` followed by `c.communicate([])` to show the loading screen. The `communicate([])` call should be sent *before* loading the scene. After loading the scene, call `vr.show_loading_screen(False)` followed by `c.communicate([])`.

### Reset

Whenever you reset a scene, you must call `vr.reset()` to re-initialize the VR add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion


class OculusLeapMotionResetScene(Controller):
    """
    Press 0 to reset the scene. Press 4 to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vr = OculusLeapMotion()
        self.vr.listen_to_button(button=0, callback=self.reset_scene)
        self.add_ons.extend([self.vr])

    def run(self) -> None:
        self.reset_scene()
        while not self.vr.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def reset_scene(self) -> None:
        self.vr.reset()
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        z = 0.6
        commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 0, "z": z},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 1, "z": z - 0.25},
                                                          scale_mass=False,
                                                          scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                          default_physics_values=False,
                                                          mass=1,
                                                          library="models_flex.json"))
        self.communicate(commands)


if __name__ == "__main__":
    c = OculusLeapMotionResetScene()
    c.run()
```

If you want to reset a scene with an explicitly-defined non-graspable object, you must set the `non_graspable` parameter in both the constructor and in `reset()`, for example:

`vr.reset(non_graspable=[object_id_0, object_id_1])`

You can set an initial position and rotation with the optional `position` and `rotation` parameters, for example:

`vr.reset(position={"x": 1, "y": 0, "z": 0.5}, rotation=30)`

## Audio

*For more information regarding audio in TDW, [read this](../audio/overview.md).*

Audio is supported in the Oculus Leap Motion rig. Unlike other audio setups in TDW, it isn't necessary to [initialize audio](../audio/initialize_audio.md); the VR rig is already set up to listen for audio.

[Resonance Audio](../audio/resonance_audio.md) is *not* supported on the Oculus Leap Motion rig. Oculus does have audio spatialization but this hasn't yet been implemented in TDW.

## Low-level commands

The `OculusLeapMotion` initializes the rig with the following commands:

- [`create_vr_rig`](../../api/command_api.md#create_vr_rig)
- [`set_vr_resolution_scale`](../../api/command_api.md#set_vr_resolution_scale)
- [`set_post_process`](../../api/command_api.md#set_post_process) (Disables post-process)
- [`send_vr_rig`](../../api/command_api.md#send_vr_rig) (Sends [`VRRig`](../../api/output_data.md#VRRig) output data every frame)
- [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig) (If `attach_avatar` in the constructor is True)
- [`set_screen_size`](../../api/command_api.md#set_screen_size) (If `attach_avatar` in the constructor is True; this sets the size of the images captured by the avatar)
- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies) (Only once, and only if `set_graspable` in the constructor is True. This will return [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies) output data, which is used to set graspable objects)
- [`set_time_step`](../../api/command_api.md#set_time_step)
- [`send_leap_moption`](../../api/command_api.md#send_leap_moption)

On the second `communicate()` call after initialization:

- Send [`ignore_leap_motion_physics_helpers`](../../api/command_api.md#ignore_leap_motion_physics_helpers) for each object that shouldn't receive physics helpers.
- Send [`set_object_collision_detection_mode`](../../api/command_api.md#set_object_collision_detection_mode), [`set_physic_material`](../../api/command_api.md#set_physic_material) for all objects that *should* receive physics helpers.
- Send [`set_mass`](../../api/command_api.md#set_mass) to adjust the mass of objects below the minimal threshold.

The add-on receives and uses the following output data:

- [`VRRig`](../../api/output_data.md#VRRig)
- [`LeapMotion`](../../api/output_data.md#LeapMotion)

- [`set_vr_loading_screen`](../../api/command_api.md#set_vr_loading_screen)

On the backend, the root body and hands are cached as objects with their own IDs (generated randomly by the build).

***

[Return to the README](../../../README.md)

***

Python API:

- [`OculusLeapMotion`](../../python/add_ons/oculus_leap_motion.md)
- [`FingerBone`](../../python/vr_data/finger_bone.md)
- [`Transform`](../../python/object_data/transform.md)
- [`ImageCapture`](../../python/add_ons/image_capture.md)

Example controllers:

- [oculus_leap_motion_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_leap_motion_minimal.py) Minimal VR example.
- [oculus_leap_motion_basket.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_leap_motion_basket.py) A minimal example of an Oculus Leap Motion rig and an item in a basket on a table.
- [oculus_leap_motion_interior_scene.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_leap_motion_interior_scene.py) Interact with objects in VR with UltraLeap hand tracking in a kitchen scene.
- [oculus_leap_motion_output_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_leap_motion_output_data.py) Add several objects to the scene and parse VR output data.
- [oculus_leap_motion_ui.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_leap_motion_ui.py) Press 0 to make the cube red. Press 4 to quit.
- [oculus_leap_motion_reset.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/vr/oculus_leap_motion_ui.py) Press 0 to reset the scene. Press 4 to quit.

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
- [`set_mass`](../../api/command_api.md#set_mass)

Output Data:

- [`VRRig`](../../api/output_data.md#VRRig)
- [`LeapMotion`](../../api/output_data.md#LeapMotion)
- [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies)
