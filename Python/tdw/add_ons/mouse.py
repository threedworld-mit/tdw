from typing import Union, List, Callable, Optional, Dict
from tdw.add_ons.add_on import AddOn
from tdw.mouse_data.mouse_button import MouseButton
from tdw.mouse_data.mouse_button_event import MouseButtonEvent
from tdw.output_data import OutputData
from tdw.output_data import Mouse as Mous


class Mouse(AddOn):
    def __init__(self):
        super().__init__()
        self._press: Dict[MouseButton, Optional[Union[Callable, List[dict]]]] = dict()
        self._hold: Dict[MouseButton, Optional[Union[Callable, List[dict]]]] = dict()
        self._release: Dict[MouseButton, Optional[Union[Callable, List[dict]]]] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_mouse",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "mous":
                mouse = Mous(resp[i])
                buttons = [b for b in MouseButton]
                for happened, button in zip([mouse.get_is_left_button_pressed(), mouse.get_is_middle_button_pressed(), mouse.get_is_right_button_pressed()],
                                            buttons):
                    self._do_event(happened, button, self._press)
                for happened, button in zip([mouse.get_is_left_button_held(), mouse.get_is_middle_button_held(), mouse.get_is_right_button_held()],
                                            buttons):
                    self._do_event(happened, button, self._hold)
                for happened, button in zip([mouse.get_is_left_button_released(), mouse.get_is_middle_button_released(), mouse.get_is_right_button_released()],
                                            buttons):
                    self._do_event(happened, button, self._release)

    def listen(self, button: Union[MouseButton, str] = MouseButton.left,
               event: Union[MouseButtonEvent, str] = MouseButtonEvent.press,
               commands: Union[dict, List[dict]] = None,
               function: Callable = None) -> None:
        """
        Listen for when a mouse button is pressed and send commands.

        :param button: The mouse button as a string or [`MouseButton`](../mouse_data/mouse_button.md).
        :param commands: Commands to be sent when the button is pressed.
        :param function: Function to invoke when the button is pressed.
        :param event: The event as a string or [`MouseButtonEvent`](../mouse_data/mouse_button_event.md).
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
        if isinstance(event, MouseButtonEvent):
            e = event
        else:
            e = MouseButtonEvent[event]
        if isinstance(button, MouseButton):
            b = button
        else:
            b = MouseButton[button]
        # Subscribe to events.
        if e == MouseButtonEvent.press:
            self._press[b] = response
        elif e == MouseButtonEvent.hold:
            self._hold[b] = response
        elif e == MouseButtonEvent.release:
            self._release[b] = response
        else:
            raise Exception(e)

    def _do_event(self, happened: bool, button: MouseButton, events: Dict[MouseButton, Optional[Union[Callable, List[dict]]]]) -> None:
        """
        Invoke an event if the button is in the events dictionary.

        :param happened: True if the mouse event happened.
        :param button: The mouse button.
        :param events: The events dictionary.
        """

        if happened and button in events:
            # Append commands to the next `communicate()` call.
            if isinstance(events[button], list):
                self.commands.extend(events[button])
            # Invoke a function.
            else:
                events[button]()
