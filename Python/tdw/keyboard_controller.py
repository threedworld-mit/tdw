from typing import List, Union
from tdw.controller import Controller
from tdw.output_data import OutputData, Keyboard


class KeyboardController(Controller):
    """
    Listen for keyboard input to send commands.

    Keyboard input is registered _from the build, not the controller._ For this controller to work, you must:

    - Run the build on the same machine as the keyboard.
    - Have the build window as the focused window (i.e. not minimized).

    Usage:

    ```python
    from tdw.keyboard_controller import KeyboardController
    from tdw.tdw_utils import TDWUtils

    def stop():
        done = True
        c.communicate({"$type": "terminate"})

    done = False
    c = KeyboardController()
    c.start()

    # Quit.
    c.listen(key="esc", function=stop)

    # Equivalent to c.start()
    c.listen(key="r", commands={"$type": "load_scene", "scene_name": "ProcGenScene"})

    while not done:
        # Receive data. Load the scene when r is pressed. Quit when Esc is pressed.
        c.communicate([])
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

        # Dictionaries of actions. Key = a keyboard key as a string.
        self._press = dict()
        self._hold = dict()
        self._release = dict()

        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate({"$type": "send_keyboard",
                          "frequency": "always"})

    def _do_event(self, k: str, events: dict) -> None:
        """
        Invoke an event if the key is in the events dictionary.

        :param k: The keyboard key as a string.
        :param events: The events dictionary.
        """

        if k in events:
            # Append commands to the next `communicate()` call.
            if isinstance(events[k], list):
                self.on_key_commands.extend(events[k])
            # Invoke a function.
            else:
                events[k]()

    def communicate(self, commands: Union[dict, List[dict]]) -> List[bytes]:
        if isinstance(commands, dict):
            commands = [commands]
        # Add commands from key presses.
        commands.extend(self.on_key_commands[:])
        # Clear the on-key commands.
        self.on_key_commands.clear()
        # Send the commands.
        resp = super().communicate(commands)

        # Get keyboard input.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "keyb":
                keys = Keyboard(resp[i])
                # Listen for events where the key was first pressed on the previous frame.
                for j in range(keys.get_num_pressed()):
                    self._do_event(k=keys.get_pressed(j), events=self._press)
                # Listen for keys currently held down.
                for j in range(keys.get_num_held()):
                    self._do_event(k=keys.get_held(j), events=self._hold)
                # Listen for keys that were released.
                for j in range(keys.get_num_released()):
                    self._do_event(k=keys.get_released(j), events=self._release)
        return resp

    def listen(self, key: str, commands: Union[dict, List[dict]] = None, function=None, events: List[str] = None) -> None:
        """
        Listen for when a key is pressed and send commands.

        :param key: The keyboard key.
        :param commands: Commands to be sent when the key is pressed.
        :param function: Function to invoke when the key is pressed.
        :param events: Listen to these keyboard events for this `key`. Options: `"press"`, `"hold"`, `"release"`. If None, this defaults to `["press"]`.
        """

        response = None
        if commands is not None:
            if isinstance(commands, dict):
                commands = [commands]
            response = commands
        elif function is not None:
            response = function
        if response is None:
            return
        if events is None:
            events = ["press"]

        # Subscribe to events.
        if "press" in events:
            self._press[key] = response
        if "hold" in events:
            self._hold[key] = response
        if "release" in events:
            self._release[key] = response

    def _set_frame_commands(self, commands: Union[dict, List[dict]]) -> None:
        """
        Set the next frame's commands.

        :param commands: The commands to send on this frame.
        """

        if isinstance(commands, dict):
            commands = [commands]
        self.on_key_commands = commands
