from typing import List
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, Raycast
from tdw.output_data import Mouse as Mous
from tdw.controller import Controller


class Mouse(AddOn):
    """
    Listen to mouse movement, button events, and whether the mouse is over an object.
    """

    def __init__(self, avatar_id: str = "a"):
        """
        :param avatar_id: The ID of the avatar. This is used to convert the mouse screen position to a world position.
        """

        super().__init__()
        """:field
        The ID of the avatar.
        """
        self.avatar_id: str = avatar_id
        """:field
        If True, the left button was pressed on this frame.
        """
        self.left_button_pressed: bool = False
        """:field
        If True, the left button was held on this frame (and pressed on a previous frame).
        """
        self.left_button_held: bool = False
        """:field
        If True, the left button was released on this frame.
        """
        self.left_button_released: bool = False
        """:field
        If True, the middle button was pressed on this frame.
        """
        self.middle_button_pressed: bool = False
        """:field
        If True, the middle button was held on this frame (and pressed on a previous frame).
        """
        self.middle_button_held: bool = False
        """:field
        If True, the middle button was released on this frame.
        """
        self.middle_button_released: bool = False
        """:field
        If True, the right button was pressed on this frame.
        """
        self.right_button_pressed: bool = False
        """:field
        If True, the right button was held on this frame (and pressed on a previous frame).
        """
        self.right_button_held: bool = False
        """:field
        If True, the right button was released on this frame.
        """
        self.right_button_released: bool = False
        """:field
        The (x, y) pixel position of the mouse on the screen.
        """
        self.screen_position: np.array = np.array([0, 0])
        """:field
        The (x, y) scroll wheel delta.
        """
        self.scroll_wheel_delta: np.array = np.array([0, 0])
        """:field
        The (x, y, z) world position of the mouse. The z depth coordinate is derived via a raycast.
        """
        self.world_position: np.array = np.array([0, 0, 0])
        """:field
        If True, the mouse is currently over an object.
        """
        self.mouse_is_over_object: bool = False
        """:field
        If `self.mouse_is_over_object == True`, this is the ID of the object.
        """
        self.mouse_over_object_id: int = -1
        """:field
        The ID of the mouse raycast.
        """
        self.raycast_id: int = Controller.get_unique_id()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_mouse",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        self.commands.append({"$type": "send_mouse_raycast",
                              "id": self.raycast_id,
                              "avatar_id": self.avatar_id})
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "mous":
                mouse = Mous(resp[i])
                # Get the screen position.
                self.screen_position = mouse.get_position()
                # Get the scroll wheel delta.
                self.scroll_wheel_delta = mouse.get_scroll_delta()
                # Get mouse button events.
                self.left_button_pressed = mouse.get_is_left_button_pressed()
                self.left_button_held = mouse.get_is_left_button_held()
                self.left_button_released = mouse.get_is_left_button_released()
                self.middle_button_pressed = mouse.get_is_middle_button_pressed()
                self.middle_button_held = mouse.get_is_middle_button_held()
                self.middle_button_released = mouse.get_is_middle_button_released()
                self.right_button_pressed = mouse.get_is_right_button_pressed()
                self.right_button_held = mouse.get_is_right_button_held()
                self.right_button_released = mouse.get_is_right_button_released()
            # Get the mouse world position raycast.
            elif r_id == "rayc":
                raycast = Raycast(resp[i])
                if raycast.get_raycast_id() == self.raycast_id:
                    self.world_position = np.array(raycast.get_point())
                    self.mouse_is_over_object = raycast.get_hit() and raycast.get_hit_object()
                    self.mouse_over_object_id = int(raycast.get_object_id())
