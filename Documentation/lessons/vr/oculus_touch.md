##### Virtual Reality (VR)

# Oculus Touch

The **Oculus Touch** is a VR rig that uses an Oculus headset (Rift, Rift S, Quest, or Quest 2) and Touch controllers. It supports head and hand tracking, grasping and dropping objects, controller button input, and teleporting around the room.

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
                                position={"x": 0, "y": 0, "z": 1.2})])
while True:
    c.communicate([])
```

### Graspable objects

By default, objects in TDW are not graspable in VR; they must be explicitly set as such via a command. The `OculusTouch` add-on sets all non-kinematic objects as graspable in VR. You can optionally disable this by setting `set_graspable=False` in the constructor:

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
                                position={"x": 0, "y": 0, "z": 1.2})])
while True:
    c.communicate([])
```

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

### Button presses

It can be useful to listen to button presses in order to trigger global events. In this example, we'll use `vr.listen()` to listen for a button press to trigger the end of the simulation:

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
        self.vr.listen(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
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

### Image and observation data

**todo and read the other thing**

## Low-level commands

