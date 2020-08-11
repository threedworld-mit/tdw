from typing import List, Union
import keyboard
from tdw.controller import Controller


class KeyboardController(Controller):
    """
    Listen for keyboard input to send commands.

    Usage:

    ```python
    from tdw.keyboard_controller import KeyboardController

    def stop():
        done = True

    done = False
    c = KeyboardController()
    c.listen(key="esc", commands={"$type": "terminate"}, function=stop)
    while not done:
        c.step() # Receive data until the Esc key is pressed.
    ```
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True, display: int = None,
                 framerate: int = 30):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        :param display: If launch_build == True, launch the build using this display number (Linux-only).
        :param framerate: The build's target frames per second.
        """

        # Commands to send on this frame.
        self.frame_commands: List[dict] = []

        super().__init__(port=port, check_version=check_version, launch_build=launch_build, display=display)

        self.communicate({"$type": "set_target_framerate",
                          "framerate": framerate})

    def step(self, commands: Union[dict, List[dict]] = None) -> List[bytes]:
        """
        Step the simulation and listen for keyboard input.
        Call this function after registering your listeners with `listen()`.

        :param commands: Any additional commands to send to the build on this frame.

        :return The response from the build.
        """

        if commands is not None:
            if isinstance(commands, dict):
                self.frame_commands.append(commands)
            else:
                self.frame_commands.extend(commands)
        # Send the commands.
        resp = self.communicate(self.frame_commands)
        # Clear the list.
        self.frame_commands.clear()
        return resp

    def listen(self, key: str, commands: Union[dict, List[dict]] = None, function=None) -> None:
        """
        Listen for when a key is pressed and send commands.

        :param key: The keyboard key.
        :param commands: Commands to be sent when the key is pressed.
        :param function: A function to be invoked when the key is pressed.
        """

        if commands is not None:
            keyboard.on_press_key(key, lambda: self._set_frame_commands(commands))
        if function is not None:
            keyboard.on_press_key(key, function)

    def _set_frame_commands(self, commands: Union[dict, List[dict]]) -> None:
        """
        Set the next frame's commands.

        :param commands: The commands to send on this frame.
        """

        if isinstance(commands, dict):
            commands = [commands]
        self.frame_commands = commands

