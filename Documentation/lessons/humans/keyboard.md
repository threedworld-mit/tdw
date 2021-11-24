##### Human user interaction

# Keyboard controls

Add keyboard controls to any controller with the [`Keyboard`](../../python/add_ons/keyboard.md) add-on:

```python
from tdw.controller import Controller
from tdw.add_ons.keyboard import Keyboard

c = Controller()
keyboard = Keyboard()
c.add_ons.append(keyboard)
```

A `Keyboard` add-on can listen for *key presses* (the key was pressed on this frame) or *key holds* (the key was pressed on a previous frame and held on this frame).

When a *key press* or *key hold* occurs, `Keyboard` can either send a command to the controller, or trigger a function.

This controller initiates an infinite loop that continues until the Escape key is pressed:

```python
from tdw.controller import Controller
from tdw.add_ons.keyboard import Keyboard

c = Controller()
keyboard = Keyboard()
c.add_ons.append(keyboard)
keyboard.listen(key="Escape", commands=[{"$type": "terminate"}])
while True:
    c.communicate([])
```

This controller does the same thing, but the `Keyboard` add-on triggers a function:

```python
from tdw.controller import Controller
from tdw.add_ons.keyboard import Keyboard


class KeyboardExample(Controller):
    """
    Minimal keyboard example. Press Escape to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = KeyboardExample()
    while not c.done:
        c.communicate([])
    c.communicate({"$type": "terminate"})
```

Note that in this example the `Keyboard` listens to a function like this:

```
keyboard.listen(key="Escape", function=self.quit)
```

*NOT* this:

```
keyboard.listen(key="Escape", function=self.quit())
```

## Keyboard controls and window focus

In order to use keyboard controls, the TDW build window must be focused (i.e. be the selected window). This means that keyboard controls will only work on personal computers.

## Control an avatar with the keyboard

In this example, the human user can control an [`EmbodiedAvatar`](../embodied_avatars/overview.md) with the keyboard.

In order to listen for both *key presses* and *key holds*, we'll set the *events* parameter like this:

```
keyboard.listen(key="UpArrow", function=self.move_forward, events=["press", "hold"])
```

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.add_ons.embodied_avatar import EmbodiedAvatar


class KeyboardControls(Controller):
    """
    Use arrow keys to move an avatar.
    """

    FORCE: float = 80
    TORQUE: float = 160

    def __init__(self, port: int = 1071):
        super().__init__(port=port)
        self.done = False

        # Add a `Keyboard` add-on to the controller to listen for keyboard input.
        keyboard: Keyboard = Keyboard()
        keyboard.listen(key="UpArrow", function=self.move_forward, events=["press", "hold"])
        keyboard.listen(key="DownArrow", function=self.move_backward, events=["press", "hold"])
        keyboard.listen(key="RightArrow", function=self.turn_right, events=["press", "hold"])
        keyboard.listen(key="LeftArrow", function=self.turn_left, events=["press", "hold"])
        keyboard.listen(key="Escape", function=self.quit, events=["press"])
        self.add_ons.append(keyboard)
        # Add an embodied avatar.
        self.embodied_avatar: EmbodiedAvatar = EmbodiedAvatar()
        self.embodied_avatar.set_drag(drag=10, angular_drag=20)
        self.add_ons.append(self.embodied_avatar)

    def move_forward(self) -> None:
        """
        Move forward.
        """

        self.embodied_avatar.apply_force(KeyboardControls.FORCE)

    def move_backward(self) -> None:
        """
        Move backward.
        """

        self.embodied_avatar.apply_force(-KeyboardControls.FORCE)

    def turn_right(self) -> None:
        """
        Turn clockwise.
        """

        self.embodied_avatar.apply_torque(KeyboardControls.TORQUE)

    def turn_left(self) -> None:
        """
        Turn counterclockwise.
        """

        self.embodied_avatar.apply_torque(-KeyboardControls.TORQUE)

    def quit(self) -> None:
        """
        End the simulation.
        """

        self.done = True

    def run(self):
        print("W, up-arrow = Move forward")
        print("S, down-arrow = Move backward")
        print("A, left-arrow = Turn counterclockwise")
        print("D, right-arrow = Turn clockwise")
        print("Esc = Quit")

        # Create the room. Set the room's floor material.
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_material("parquet_alternating_orange", library="materials_high.json"),
                         {"$type": "set_proc_gen_floor_material",
                          "name": "parquet_alternating_orange"},
                         {"$type": "set_proc_gen_floor_texture_scale",
                          "scale": {"x": 8, "y": 8}}])
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    KeyboardControls().run()

```

## Low-level API

The `Keyboard` add-on sends [`send_keyboard`](../../api/command_api.md#send_keyboard) in order to receive [`Keyboard`](../../api/output_data.md#Keyboard) output data per-frame. You could feasibly use `send_keyboard` to develop your own listener system. In practice, the `Keyboard` add-on should be sufficient for nearly all use-cases.

***

**Next: [Virtual reality](vr.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [keyboard_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/humans/keyboard_minimal.py) Minimal keyboard example. Press Escape to quit.
- [keyboard_controls.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/humans/keyboard_controls.py) Use arrow keys to move an avatar.

Python API:

- [`Keyboard`](../../python/add_ons/keyboard.md)

Command API:

- [`send_keyboard`](../../api/command_api.md#send_keyboard)

Output data:

- [`Keyboard`](../../api/output_data.md#Keyboard)