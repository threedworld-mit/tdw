import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, AvatarKinematic, Mouse


class FirstPersonAvatar(AddOn):
    def listen(self, burr, commands: Union[dict, List[dict]] = None, function: Callable = None,
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