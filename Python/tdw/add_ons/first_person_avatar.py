from os import urandom
from base64 import b64encode
from io import BytesIO
from secrets import token_urlsafe
from typing import Dict, Optional, List
import numpy as np
from PIL import Image
from tdw.add_ons.mouse import Mouse
from tdw.add_ons.third_person_camera_base import ThirdPersonCameraBase
from tdw.output_data import OutputData, AvatarKinematic
from tdw.object_data.transform import Transform


class FirstPersonAvatar(Mouse):
    """
    An avatar that can be moved via keyboard and mouse controls. This is a subclass of [`Mouse`](mouse.md).

    A `FirstPersonAvatar` includes the position of the avatar, and screen and world position of the mouse, the object ID of the object under the mouse (if any), and mouse button events.
    You can combine a `FirstPersonAvatar` with [`ImageCapture`](image_capture.md) to receive image data.
    """

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None, rotation: float = 0,
                 field_of_view: int = None, height: float = 1.6, camera_height: float = 1.6, radius: float = 0.5,
                 slope_limit: float = 15, detect_collisions: bool = True, move_speed: float = 1.5, look_speed: float = 50,
                 look_x_limit: float = 45, framerate: int = 60, reticule_size: int = 9):
        """
        :param avatar_id: The ID of the avatar. If None, a random ID is generated.
        :param position: The initial position of the avatar. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the avatar in degrees.
        :param field_of_view: If not None, set the field of view.
        :param height: The height of the avatar.
        :param camera_height: The height of the avatar's camera.
        :param radius: The radius of the avatar.
        :param slope_limit: The avatar can only climb slopes up to this many degrees.
        :param detect_collisions: If True, the avatar will collide with other objects.
        :param move_speed: The move speed in meters per second.
        :param look_speed: The camera rotation speed in degrees per second.
        :param look_x_limit: The camera rotation limit around the x axis in degrees.
        :param framerate: The target framerate.
        :param reticule_size: The size of the camera reticule in pixels. If None, no reticule will be shown.
        """

        # Set a random avatar ID.
        if avatar_id is None:
            avatar_id: str = token_urlsafe(4)
        # Set the render order.
        self._render_order: int = ThirdPersonCameraBase.RENDER_ORDER
        ThirdPersonCameraBase.RENDER_ORDER += 1
        # The initial position.
        self._initial_position: Optional[Dict[str, float]] = position
        # The initial rotation.
        self._initial_rotation: float = rotation
        # The field of view.
        self._field_of_view: Optional[float] = field_of_view
        self._height: float = height
        self._camera_height: float = camera_height
        self._radius: float = radius
        self._slope_limit: float = slope_limit
        self._detect_collisions: float = detect_collisions
        self._move_speed: float = move_speed
        self._look_speed: float = look_speed
        self._look_x_limit: float = look_x_limit
        self._framerate: int = framerate
        self._reticule_size: int = reticule_size
        self._raycast_id: int = int.from_bytes(urandom(3), byteorder='big')
        """:field
        The [`Transform`](../object_data/transform.md) of the avatar.
        """
        self.transform: Optional[Transform] = None
        super().__init__(avatar_id=avatar_id)

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "create_avatar",
                     "type": "A_First_Person",
                     "id": self.avatar_id},
                    {"$type": "set_first_person_avatar",
                     "avatar_id": self.avatar_id,
                     "height": self._height,
                     "camera_height": self._camera_height,
                     "radius": self._radius,
                     "slope_limit": self._slope_limit,
                     "detect_collisions": self._detect_collisions,
                     "move_speed": self._move_speed,
                     "look_speed": self._look_speed,
                     "look_x_limit": self._look_x_limit},
                    {"$type": "set_target_framerate",
                     "framerate": self._framerate},
                    {"$type": "set_render_order",
                     "render_order": self._render_order,
                     "avatar_id": self.avatar_id},
                    {"$type": "set_cursor",
                     "locked": True,
                     "visible": False},
                    {"$type": "send_avatars",
                     "frequency": "always"}]
        # Set the initial position.
        if self._initial_position is not None:
            commands.append({"$type": "teleport_avatar_to",
                             "position": self._initial_position,
                             "avatar_id": self.avatar_id})
        # Set the initial rotation.
        if self._initial_rotation is not None:
            commands.append({"$type": "rotate_avatar_to_euler_angles",
                             "euler_angles": {"x": 0, "y": self._initial_rotation, "z": 0},
                             "avatar_id": self.avatar_id})
        # Set the field of view.
        if self._field_of_view is not None:
            commands.append({"$type": "set_field_of_view",
                             "field_of_view": self._field_of_view,
                             "avatar_id": self.avatar_id})
        commands.extend(super().get_initialization_commands())
        # Add a reticule.
        if self._reticule_size > 0:
            # Create a reticule.
            arr = np.zeros(shape=(self._reticule_size, self._reticule_size), dtype=np.uint8)
            x = np.arange(0, arr.shape[0])
            y = np.arange(0, arr.shape[1])
            # Define a circle on the array.
            r = self._reticule_size // 2
            mask = ((x[np.newaxis, :] - r) ** 2 + (y[:, np.newaxis] - r) ** 2 < r ** 2)
            # Set the color of the reticule.
            arr[mask] = 200
            arr = np.stack((arr,) * 4, axis=-1)
            # Convert to a .png byte array. Source: https://stackoverflow.com/a/38626806
            with BytesIO() as output:
                Image.fromarray(arr).save(output, "PNG")
                image = output.getvalue()
            canvas_id = self._raycast_id
            # Add a reticule UI element.
            commands.extend([{"$type": "add_ui_canvas",
                              "canvas_id": canvas_id},
                             {"$type": "attach_ui_canvas_to_avatar",
                              "avatar_id": self.avatar_id,
                              "canvas_id": canvas_id},
                             {"$type": "add_ui_image",
                              "image": b64encode(image).decode("utf-8"),
                              "size": {"x": self._reticule_size, "y": self._reticule_size},
                              "rgba": True,
                              "id": 0,
                              "raycast_target": False,
                              "canvas_id": canvas_id}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get the avatar's transform data.
            if r_id == "avki":
                avatar_kinematic = AvatarKinematic(resp[i])
                if avatar_kinematic.get_avatar_id() == self.avatar_id:
                    self.transform = Transform(position=np.array(avatar_kinematic.get_position()),
                                               rotation=np.array(avatar_kinematic.get_rotation()),
                                               forward=np.array(avatar_kinematic.get_forward()))

    def reset(self, position: Dict[str, float] = None, rotation: float = 0, field_of_view: int = None) -> None:
        """
        Reset the avatar. Call this whenever the scene resets.

        :param position: The initial position of the avatar. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the avatar in degrees.
        :param field_of_view: If not None, set the field of view.
        """

        self.commands.clear()
        self.initialized = False
        self._initial_position = position
        self._initial_rotation = rotation
        self._field_of_view = field_of_view
