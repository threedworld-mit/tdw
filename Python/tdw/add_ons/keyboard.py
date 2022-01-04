from typing import List, Union, Callable, Optional, Dict
from tdw.output_data import OutputData
from tdw.output_data import Keyboard as KBoard
from tdw.add_ons.add_on import AddOn


class Keyboard(AddOn):
    """
    Add keyboard controls to a TDW scene.
    """

    def __init__(self):
        super().__init__()
        self._press: Dict[str, Optional[Union[Callable, List[dict]]]] = dict()
        self._hold: Dict[str, Optional[Union[Callable, List[dict]]]] = dict()
        self._release: Dict[str, Optional[Union[Callable, List[dict]]]] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_keyboard",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        # Get keyboard input.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "keyb":
                keys = KBoard(resp[i])
                # Listen for events where the key was first pressed on the previous frame.
                for j in range(keys.get_num_pressed()):
                    self._do_event(k=keys.get_pressed(j), events=self._press)
                # Listen for keys currently held down.
                for j in range(keys.get_num_held()):
                    self._do_event(k=keys.get_held(j), events=self._hold)
                # Listen for keys that were released.
                for j in range(keys.get_num_released()):
                    self._do_event(k=keys.get_released(j), events=self._release)

    def listen(self, key: str, commands: Union[dict, List[dict]] = None, function: Callable = None,
               events: List[str] = None) -> None:
        """
        Listen for when a key is pressed and send commands.

        :param key: The keyboard key.
        :param commands: Commands to be sent when the key is pressed.
        :param function: Function to invoke when the key is pressed.
        :param events: Listen to these keyboard events for this `key`. Options: `"press"`, `"hold"`, `"release"`. If None, this defaults to `["press"]`.
        """

        response: Optional[Union[Callable, List[dict]]] = None
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

    def _do_event(self, k: str, events: dict) -> None:
        """
        Invoke an event if the key is in the events dictionary.

        :param k: The keyboard key as a string.
        :param events: The events dictionary.
        """

        if k in events:
            # Append commands to the next `communicate()` call.
            if isinstance(events[k], list):
                self.commands.extend(events[k])
            # Invoke a function.
            else:
                events[k]()
