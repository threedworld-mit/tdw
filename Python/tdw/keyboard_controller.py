from typing import List, Union
import keyboard
from tdw.controller import Controller


class KeyboardController(Controller):
    """
    Listen for keyboard input to send commands.

    Usage:

    ```python
    from tdw.keyboard_controller import KeyboardController
    from tdw.tdw_utils import TDWUtils

    def stop():
        done = True

    done = False
    c = KeyboardController()
    c.start()

    # Quit.
    c.listen(key="esc", commands=None, function=stop)

    # Equivalent to c.start()
    c.listen(key="r", commands={"$type": "load_scene", "scene_name": "ProcGenScene"}, function=None)

    while not done:
        # Receive data. Load the scene when r is pressed. Quit when Esc is pressed.
        c.communicate([])
    # Stop the build.
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        """

        # Commands that should be added due to key presses on this frame.
        self.on_key_commands: List[dict] = []

        super().__init__(port=port, check_version=check_version, launch_build=launch_build)

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        if isinstance(commands, dict):
            commands = [commands]
        # Add commands from key presses.
        commands.extend(self.on_key_commands[:])
        # Clear the on-key commands.
        self.on_key_commands.clear()
        return super().communicate(commands)

    def listen(self, key: str, commands: Union[dict, List[dict]] = None, function=None) -> None:
        """
        Listen for when a key is pressed and send commands.

        :param key: The keyboard key.
        :param commands: Commands to be sent when the key is pressed.
        :param function: A function to be invoked when the key is pressed.
        """

        if commands is not None:
            keyboard.on_press_key(key, lambda e: self._set_frame_commands(commands))
        if function is not None:
            keyboard.on_press_key(key, lambda e: function())

    def _set_frame_commands(self, commands: Union[dict, List[dict]]) -> None:
        """
        Set the next frame's commands.

        :param commands: The commands to send on this frame.
        """

        if isinstance(commands, dict):
            commands = [commands]
        self.on_key_commands = commands

