##### Keyboard controls

# Keyboard input

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

## Low-level API

The `Keyboard` add-on sends [`send_keyboard`](../../api/command_api.md#send_keyboard) in order to receive [`Keyboard`](../../api/output_data.md#Keyboard) output data per-frame. You could feasibly use `send_keyboard` to develop your own listener system. In practice, the `Keyboard` add-on should be sufficient for nearly all use-cases.

***

**This is the last document in the "Keyboard and Mouse" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [keyboard_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/keyboard_and_mouse/keyboard_minimal.py) Minimal keyboard example. Press Escape to quit.

Python API:

- [`Keyboard`](../../python/add_ons/keyboard.md)

Command API:

- [`send_keyboard`](../../api/command_api.md#send_keyboard)

Output data:

- [`Keyboard`](../../api/output_data.md#Keyboard)