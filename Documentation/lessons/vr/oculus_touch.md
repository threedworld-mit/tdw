##### Virtual Reality (VR)

# Oculus Touch

The **Oculus Touch** is a VR rig that uses an Oculus headset and Touch controllers. It supports head and hand tracking, grasping and dropping objects, controller button input, and teleporting around the room.

## Requirements

- Windows 10
- [A compatible GPU](https://support.oculus.com/articles/headsets-and-accessories/oculus-link/oculus-link-compatibility/)
- Oculus headset (Rift, Rift S, Quest, or Quest 2)
- *Quest and Quest 2:* An Oculus Link Cable
  - A USB-C port
- [The Oculus PC app](https://www.oculus.com/setup/)

## Setup

After installing the Oculus PC app, you must run it while running the controller and the build.

## Rig description

The Oculus Touch VR rig has two floating hands. The hands can interact with objects either by pushing them (the hands have colliders and Rigidbodies) or by grabbing them. The hands may be "robot" hands or "human" hands. The rig has a small collider on the floor and a head camera. The head, torso, legs, etc. don't have visual meshes or physics colliders.

## Controls

![](images/oculus_touch/controls.png)

*[Source](https://circuitstream.com/blog/oculus-unity-setup/)*

| Button                | Effect                                                       |
| --------------------- | ------------------------------------------------------------ |
| grip_button (left)    | Grab or drop an object with the left hand.                   |
| grip_button (right)   | Grab or drop an object with the right hand.                  |
| primary_2d_axis_click | Click and hold to set a position to teleport to. Release to teleport. |

## The `OculusTouch` add-on

The simplest way to add an Oculus Touch rig to the scene is to use the [`OculusTouch` add-on](../../python/add_ons/oculus_touch.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch

c = Controller()
vr = OculusTouch()
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
```

Result:

![](images/oculus_touch/minimal.gif)

### Button presses

It can be useful to listen to button presses in order to trigger global events. In this example, we'll use `vr.listen_to_button()` to listen for a button press to trigger the end of the simulation. Note that the `button` parameter accepts an [`OculusTouchButton`](../../python/vr_data/oculus_touch_button.md) value.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.vr_data.oculus_touch_button import OculusTouchButton


class VirtualReality(Controller):
    """
    Minimal VR example.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        self.vr = OculusTouch()
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        self.add_ons.extend([self.vr])

    def run(self) -> None:
        object_id = self.get_unique_id()
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_object(model_name="rh10",
                                              object_id=object_id,
                                              position={"x": 0, "y": 0, "z": 1.2})])
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VirtualReality()
    c.run()
```

This somewhat more complicated example creates "trials" of different objects in the scene whenever a button is pressed:

```python
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.vr_data.oculus_touch_button import OculusTouchButton


class OculusTouchButtonListener(Controller):
    """
    Listen for button presses to reset the scene.
    """

    MODEL_NAMES = ["rh10", "iron_box", "trunck"]

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.simulation_done = False
        self.trial_done = False
        self.vr = OculusTouch()
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        # End the trial when the right trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=False, function=self.end_trial)
        self.add_ons.extend([self.vr])
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def trial(self) -> None:
        # Start a new trial.
        self.trial_done = False
        # Choose a random model.
        model_name = random.choice(OculusTouchButtonListener.MODEL_NAMES)
        # Add the model.
        object_id = self.get_unique_id()
        self.communicate(self.get_add_object(model_name=model_name,
                                             object_id=object_id,
                                             position={"x": 0, "y": 0, "z": 1.2}))
        # Wait until the trial is done.
        while not self.trial_done and not self.simulation_done:
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})

    def run(self) -> None:
        while not self.simulation_done:
            # Run a trial.
            self.trial()
        # End the simulation.
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.simulation_done = True

    def end_trial(self):
        self.trial_done = True


if __name__ == "__main__":
    c = OculusTouchButtonListener()
    c.run()
```

Result:

![](images/oculus_touch/button_listener.gif)

### Graspable objects

By default, objects in TDW are not graspable in VR; they must be explicitly set as such via a command. **The `OculusTouch` add-on sets all non-kinematic objects as graspable in VR.** You can optionally disable this by setting `set_graspable=False` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch

c = Controller()
vr = OculusTouch(set_graspable=False)
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
```

### Composite objects

It is possible to grasp [composite sub-objects](../physx/composite_objects.md) such as the door of a microwave in VR. The VR system automatically finds 'affordance points' for the hands to grasp. The resulting motion may at times be jittery; this is due to the underlying hand tracking and object grasping system:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.vr_data.oculus_touch_button import OculusTouchButton


class OculusTouchCompositeObject(Controller):
    """
    Manipulate a composite object in VR.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self.done = False
        # Add the VR rig.
        self.vr = OculusTouch(human_hands=False, output_data=True, attach_avatar=True, set_graspable=False)
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        self.add_ons.append(self.vr)

    def run(self) -> None:
        self.communicate(Controller.get_add_physics_object(model_name="vm_v5_072_composite",
                                                           object_id=Controller.get_unique_id(),
                                                           position={"x": 0, "y": 0.7, "z": 0.9},
                                                           kinematic=True))
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = OculusTouchCompositeObject()
    c.run()
```

Result:

![](images/oculus_touch/composite_object.gif)

### Output data

The `OculusTouch` add-on saves the head, rig base, and hands data per-frame as [`Transform` objects](../../python/object_data/transform.md). `vr.held_left` and `vr.held_right` are arrays of IDs of objects held in the left and right hands:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch

c = Controller()
vr = OculusTouch()
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 1.2})])
while True:
    print(vr.rig.position)
    print(vr.head.position)
    print(vr.left_hand.position)
    print(vr.right_hand.position)
    print(vr.held_left, vr.held_right)
    c.communicate([])
```

You can disable output data by setting `output_data=False` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch

c = Controller()
vr = OculusTouch(output_data=False)
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 1.2})])
while True:
    c.communicate([])
```

### Image capture

VR rig cameras are not [avatars](../core_concepts/avatars.md).  You can attach an avatar to a VR rig by setting `attach_avatar=True` in the constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch

c = Controller()
vr = OculusTouch(attach_avatar=True)
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
while True:
    c.communicate([])
```

You can then adjust the camera and capture image data like with any other avatar. The ID of this avatar is always `"vr"`.

For performance reasons, the default width of the avatar's images is 512, which is lower than the resolution of the headset. The height is always scaled proportional to the width. To adjust the pixel width and height ratio, set `avatar_camera_width` and `headset_aspect_ratio` in the constructor.

### Hand models

The Oculus Touch rig has two hand models:

1. Human-like hands
2. Robot-like hands

Set the hand model with the optional constructor parameter `human_hands` (default is True).

### Teleport and rotate the VR rig

You can "teleport" around your scene by clicking down the left control stick; release to teleport to the location at the end of the rendered arc. This can be useful when your virtual scene space is larger than your real-world (Guardian) space, and you cannot simply walk to certain areas within your virtual space. You can programatically set the rig's position in the scene with `vr.set_position(position)`. This can be useful for initially placing yourself at a particular location within your scene.

You can rotate the rig by physically turning your body. You can programatically rotate the rig with `vr.rotate_by(angle)`. This can be useful for setting the initial rotation of the rig, in order to start off facing a particular direction in your scene. 

### Reset

Whenever a new scene is loaded, you must call `vr.reset()` to re-initialize the VR add-on:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch

c = Controller()
vr = OculusTouch()
c.add_ons.append(vr)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="rh10",
                                object_id=Controller.get_unique_id(),
                                position={"x": 0, "y": 0, "z": 0.5})])
vr.reset()
c.communicate([{"$type": "load_scene",
                "scene_name": "ProcGenScene"},
               TDWUtils.create_empty_room(12, 12)])
c.communicate({"$type" : "terminate"})
```

## Collision detection

*For more information regarding collision detection, [read this](../physx/collisions.md).*

The Oculus Touch rig can send basic haptics data. The rig has a small collider at its base. Each palm has a Rigidbody and a collider. The base and the palms will be detected if [collision detection is enabled](../physx/collisions.md) as if they were standard TDW objects. If you are using [PyImpact](../audio/py_impact.md) (see below), tapping your hands together will create a faint sound.

## Audio

*For more information regarding audio in TDW, [read this](../audio/overview.md).*

Audio is supported in the Oculus Touch rig. Unlike other audio setups in TDW, it isn't necessary to [initialize audio](../audio/initialize_audio.md); the VR rig is already set up to listen for audio.

[Resonance Audio](../audio/resonance_audio.md) is *not* supported on the Oculus Touch rig. Oculus does have audio spatialization but this hasn't yet been implemented in TDW.

This example controller adds an Oculus Touch rig and [PyImpact](../audio/py_impact.md) to a scene:

```python
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.add_ons.py_impact import PyImpact
from tdw.vr_data.oculus_touch_button import OculusTouchButton


class OculusTouchPyImpact(Controller):
    """
    Listen to audio generated by PyImpact.
    """

    MODEL_NAMES = ["rh10", "iron_box", "trunck"]

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.simulation_done = False
        self.trial_done = False
        self.vr = OculusTouch(set_graspable=False)
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        # End the trial when the right trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=False, function=self.end_trial)
        # Enable PyImpact.
        self.py_impact = PyImpact()
        self.add_ons.extend([self.vr, self.py_impact])
        self.communicate(TDWUtils.create_empty_room(12, 12))

    def trial(self) -> None:
        # Start a new trial.
        self.trial_done = False
        # Reset PyImpact.
        self.py_impact.reset()
        # Choose a random model.
        model_name = random.choice(OculusTouchPyImpact.MODEL_NAMES)
        # Add the model.
        object_id_0 = Controller.get_unique_id()
        commands = Controller.get_add_physics_object(model_name=model_name,
                                                     object_id=object_id_0,
                                                     position={"x": 0, "y": 0, "z": 1.2})
        object_id_1 = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name="vase_02",
                                                          position={"x": 0, "y": 3, "z": 1.2},
                                                          object_id=object_id_1))
        self.communicate(commands)
        # Wait until the trial is done.
        while not self.trial_done and not self.simulation_done:
            self.communicate([])
        # Destroy the object.
        self.communicate([{"$type": "destroy_object",
                           "id": object_id_0},
                          {"$type": "destroy_object",
                           "id": object_id_1}])

    def run(self) -> None:
        while not self.simulation_done:
            # Run a trial.
            self.trial()
        # End the simulation.
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.simulation_done = True

    def end_trial(self):
        self.trial_done = True


if __name__ == "__main__":
    c = OculusTouchPyImpact()
    c.run()
```

## Low-level commands

The `OculusTouchRig` initializes the rig with the following commands:

- [`create_vr_rig`](../../api/command_api.md#create_vr_rig)
- [`set_vr_resolution_scale`](../../api/command_api.md#set_vr_resolution_scale)
- [`set_post_process`](../../api/command_api.md#set_post_process) (Disables post-process)
- [`send_vr_rig`](../../api/command_api.md#send_vr_rig) (Sends [`VRRig`](../../api/output_data.md#VRRig) output data every frame)
- [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig) (If `attach_avatar` in the constructor is True)
- [`set_screen_size`](../../api/command_api.md#set_screen_size) (If `attach_avatar` in the constructor is True; this sets the size of the images captured by the avatar)
- [`send_static_rigidbodies`](../../api/command_api.md#send_static_rigidbodies) (Only once, and only if `set_graspable` in the constructor is True. This will return [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies) output data, which is used to set graspable objects)
- [`send_oculus_touch_buttons`](../../api/command_api.md#send_oculus_touch_buttons) (Sends [`OculusTouchButtons`](../../api/output_data.md#OculusTouchButtons) output data every frame)

On the second `communicate()` call after initialization:

- Using `StaticRigidbodies` data, send [`set_vr_graspable`](../../api/command_api.md#set_vr_graspable) for each non-kinematic object in the scene.

Position and rotation:

- [`teleport_vr_rig`](../../api/command_api.md#teleport_vr_rig)
- [`rotate_vr_rig_by`](../../api/command_api.md#rotate_vr_rig_by)

On the backend, the root body and hands are cached as objects with their own IDs (generated randomly by the build). `PyImpact` will automatically search for the Oculus Touch rig's object IDs by sending [`send_static_oculus_touch`](../../api/command_api.md#send_static_oculus_touch) which returns [`StaticOculusTouch`](../../api/output_data.md#StaticOculusTouch). This data is *only* used by `PyImpact` (it is *not* used by `OculusTouchRig`) though in the future it might have other useful applications.

***

**This is the last document in the "Virtual Reality (VR)" tutorial.**

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

Output Data:

- [`VRRig`](../../api/output_data.md#VRRig)
- [`OculusTouchButtons`](../../api/output_data.md#OculusTouchButtons)
- [`StaticRigidbodies`](../../api/output_data.md#StaticRigidbodies)
- [`StaticOculusTouch`](../../api/output_data.md#StaticOculusTouch)
