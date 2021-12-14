##### Human user interaction

# Virtual reality

It is possible for a human to interact with a TDW scene using virtual reality (VR).

## Requirements

- Oculus VR with Touch controls. *In the future, more VR hardware will be supported in TDW.*
- Windows
- A GPU that can run at 90 FPS or more on a VR headset.

## Add a VR rig to a scene

You can enable virtual reality (VR) in TDW by sending [`create_vr_rig`](../../api/command_api.md#create_vr_rig):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_vr_rig"}])
```

VR rig movement does *not* conform to TDW's frame stepping; in other words, it is possible to move in VR in between `c.communicate()` calls or even if `c.communicate()` is never called.

In order to advance the simulation during a VR simulation, you must continuously call `c.communicate()`. 

In this example, a VR rig is added to the scene. The scene continues until [the Escape key is pressed](keyboard.md).

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard


class VirtualReality(Controller):
    """
    Minimal VR example. Press Escape to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False

        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)

    def run(self) -> None:
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "create_vr_rig"}])
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VirtualReality()
    c.run()
```

## Pick up objects in VR

In order to pick up objects in VR, you must first make the object "graspable" by sending [`set_graspable`](../../api/command_api.md#set_graspable):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard


class VirtualReality(Controller):
    """
    Minimal VR example. Press Escape to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False

        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)

    def run(self) -> None:
        object_id = self.get_unique_id()
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "create_vr_rig"},
                          self.get_add_object(model_name="rh10",
                                              object_id=object_id,
                                              position={"x": 0, "y": 0, "z": 1.2}),
                          {"$type": "set_graspable", 
                           "id": object_id}])
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VirtualReality()
    c.run()
```

## Output data

Send [`send_vr_rig`](../../api/command_api.md#send_vr_rig) in order to receive [`VRRig`](../../api/output_data.md#VRRig) output data. This data includes the position of the root object of the VR rig and the position, forward, and rotation of each hand and of the head:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.output_data import OutputData, VRRig


class VRData(Controller):
    """
    Add several objects to the scene and parse VR output data.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False

        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the table object and make it kinematic.
        commands.extend(self.get_add_physics_object(model_name="small_table_green_marble",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0, "y": 0, "z": 0.5},
                                                    kinematic=True,
                                                    library="models_core.json"))
        # Add a box object and make it graspable.
        box_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="woven_box",
                                                    object_id=box_id,
                                                    position={"x": 0.2, "y": 1.0, "z": 0.5},
                                                    library="models_core.json"))
        self.communicate([{"$type": "set_graspable",
                           "id": box_id}])
        # Add the ball object and make it graspable.
        sphere_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                                                    object_id=sphere_id,
                                                    position={"x": 0.2, "y": 3.0, "z": 0.5},
                                                    library="models_special.json",
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2}))
        commands.append({"$type": "set_graspable",
                         "id": sphere_id})
        # Receive VR data per frame.
        commands.append({"$type": "send_vr_rig",
                         "frequency": "always"})
        # Send the commands.
        resp = self.communicate(commands)
        # Loop until the Escape key is pressed.
        while not self.done:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse VR data.
                if r_id == "vrri":
                    vr_rig = VRRig(resp[i])
                    print("Position", vr_rig.get_position())
                    print("Rotation", vr_rig.get_rotation())
                    print("Forward", vr_rig.get_forward())
                    
                    print("Head position", vr_rig.get_head_position())
                    print("Head rotation", vr_rig.get_head_rotation())
                    print("Head forward", vr_rig.get_head_forward())
                    
                    print("Left hand position", vr_rig.get_left_hand_position())
                    print("Left hand rotation", vr_rig.get_left_hand_rotation())
                    print("Left hand forward", vr_rig.get_left_hand_forward())
                    
                    print("Right hand position", vr_rig.get_right_hand_position())
                    print("Right hand rotation", vr_rig.get_right_hand_rotation())
                    print("Right hand forward", vr_rig.get_right_hand_forward())
                    
                    print("")
            resp = self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VRData()
    c.run()
```

## VR Image data

VR rigs don't return [`Images`](../../api/output_data.md#Images) data because they aren't [avatars](../core_concepts/avatars.md). You can attach an avatar to a VR rig with the command [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig). This command *creates* the avatar as well as *attaches* it to the VR rig.

There is a tradeoff: Because the VR headset renders at a high resolution, the framerate can drop significantly when receiving [image observation data](../visual_perception/overview.md).

In this example, several objects are added to the scene. An avatar is attached to the VR rig. The controller requests [`IdPassSegmentationColors`](../../api/output_data.md#IdPassSegmentationColors) output data from the avatar's camera. Per frame, the controller logs the names of all visible objects and the rotation of the VR rig's head. When the Escape key is pressed, the simulation ends and a log of the frame data is saved:

```python
from typing import List, Dict
from json import dumps
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.output_data import OutputData, VRRig, IdPassSegmentationColors, SegmentationColors


class VRObservedObjects(Controller):
    """
    Add several objects to the scene. Record which objects are visible to the VR agent.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)
        self.segmentation_colors: Dict[tuple, str] = dict()
        self.frame_data: List[dict] = list()

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the table object and make it kinematic.
        commands.extend(self.get_add_physics_object(model_name="small_table_green_marble",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0, "y": 0, "z": 0.5},
                                                    kinematic=True,
                                                    library="models_core.json"))
        # Add a box object and make it graspable.
        box_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="woven_box",
                                                    object_id=box_id,
                                                    position={"x": 0.2, "y": 1.0, "z": 0.5},
                                                    library="models_core.json"))
        self.communicate([{"$type": "set_graspable",
                           "id": box_id}])
        # Add the ball object and make it graspable.
        sphere_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                                                    object_id=sphere_id,
                                                    position={"x": 0.2, "y": 3.0, "z": 0.5},
                                                    library="models_special.json",
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2}))
        commands.append({"$type": "set_graspable",
                         "id": sphere_id})
        # Receive VR data per frame.
        # Receive segmentation colors data only on this frame.
        # Reduce render quality in order to improve framerate.
        # Attach an avatar to the VR rig.
        # Request the colors of objects currently observed by the avatar per frame.
        commands.extend([{"$type": "send_vr_rig",
                         "frequency": "always"},
                         {"$type": "send_segmentation_colors"},
                         {"$type": "set_post_process",
                          "value": False},
                         {"$type": "set_render_quality",
                          "render_quality": 0},
                         {"$type": "attach_avatar_to_vr_rig",
                          "id": "a"},
                         {"$type": "send_id_pass_segmentation_colors",
                          "frequency": "always"}])
        # Send the commands.
        resp = self.communicate(commands)
        # Record the segmentation colors.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "segm":
                segm = SegmentationColors(resp[i])
                for j in range(segm.get_num()):
                    self.segmentation_colors[segm.get_object_color(j)] = segm.get_object_name(j)
        # Loop until the Escape key is pressed.
        while not self.done:
            head_rotation = (0, 0, 0, 0)
            visible_objects = []
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse VR data.
                if r_id == "vrri":
                    vr_rig = VRRig(resp[i])
                    head_rotation = vr_rig.get_head_rotation()
                # Evaluate what objects are visible.
                elif r_id == "ipsc":
                    ipsc = IdPassSegmentationColors(resp[i])
                    for j in range(ipsc.get_num_segmentation_colors()):
                        color = ipsc.get_segmentation_color(j)
                        object_name = self.segmentation_colors[color]
                        visible_objects.append(object_name)
            # Record this frame.
            self.frame_data.append({"head_rotation": head_rotation,
                                    "visible_objects": visible_objects})
            # Advance to the next frame.
            resp = self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True
        # Write the record to disk.
        Path("log.json").write_text(dumps(self.frame_data))


if __name__ == "__main__":
    c = VRObservedObjects()
    c.run()
```

## VR and Flex

It is *technically* possible to use a VR agent in a [Flex simulation](../flex/flex.md). However,  the particles of a "held" object will have no velocity (0, 0, 0).

## Other VR commands

| Command                                                      | Description                     |
| ------------------------------------------------------------ | ------------------------------- |
| [`teleport_vr_rig`](../../api/command_api.md#teleport_vr_rig) | Set the position of the VR rig. |
| [`destroy_vr_rig`](../../api/command_api.md#destroy_vr_rig)  | Destroy the VR rig.             |

## Roadmap

In addition to continuously providing more stable support of existing VR hardware, we will in the future add support for more hardware as well as "embodied" VR rigs that have a visible body.

***

**This is the last document in the "Human user interaction" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [vr_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/humans/vr_minimal.py) Minimal VR example. Press Escape to quit.
- [vr_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/humans/vr_data.py) Add several objects to the scene and parse VR output data.
- [vr_observed_objects.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/humans/vr_observed_objects.py) Add several objects to the scene. Record which objects are visible to the VR agent.

Command API:

- [`create_vr_rig`](../../api/command_api.md#create_vr_rig)
- [`set_graspable`](../../api/command_api.md#set_graspable)
- [`send_vr_rig`](../../api/command_api.md#send_vr_rig)
- [`attach_avatar_to_vr_rig`](../../api/command_api.md#attach_avatar_to_vr_rig)
- [`teleport_vr_rig`](../../api/command_api.md#teleport_vr_rig)
- [`destroy_vr_rig`](../../api/command_api.md#destroy_vr_rig)

Output data:

- [`VRRig`](../../api/output_data.md#VRRig)
- [`IdPassSegmentationColors`](../../api/output_data.md#IdPassSegmentationColors)
- [`Images`](../../api/output_data.md#Images)