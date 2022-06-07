##### Keyboard and Mouse

# Overview

TDW includes support for keyboard and mouse input.

In order to use keyboard and mouse controls, the TDW build window must be focused (i.e. be the selected window). This means that keyboard controls will only work on personal computers.

TDW divides keyboard and mouse input into three "layers":

1. [Mouse input](mouse.md), which includes button presses, releases, etc. as well as the position of the mouse and any object underneath the cursor. This is handled via the `Mouse` add-on.
2. [A first-person avatar](first_person_avatar.md) that moves and rotates via keyboard and mouse controls. This is handled via the `FirstPersonAvatar` add-on, a subclass of `Mouse`.
3. [Keyboard input](keyboard.md) for listening to arbitrary key events. This is handled via the `Keyboard` add-on.

***

**Next: [Mouse input](mouse.md)**

[Return to the README](../../../README.md)