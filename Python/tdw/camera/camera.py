from typing import List, Dict, Optional
from tdw.tdw_utils import TDWUtils
from tdw.camera.move_target import MoveTarget
from tdw.camera.rotate_target import RotateTarget
from tdw.camera.focus_target import FocusTarget


class Camera:
    # The render order for the next camera.
    RENDER_ORDER: int = 100

    def __init__(self, avatar_id: str, images: bool = False, pass_masks: List[str] = None):
        self.avatar_id: str = avatar_id
        # These commands are sent exactly once (on the next frame).
        self._next_frame_commands: List[dict] = [{"$type": "create_avatar",
                                                  "type": "A_Img_Caps_Kinematic",
                                                  "id": self.avatar_id},
                                                 {"$type": "set_anti_aliasing",
                                                  "mode": "subpixel",
                                                  "avatar_id": self.avatar_id},
                                                 {"$type": "set_render_order",
                                                  "render_order": Camera.RENDER_ORDER,
                                                  "avatar_id": self.avatar_id},
                                                 {"$type": "send_transforms",
                                                  "frequency": "always"},
                                                 {"$type": "send_avatars",
                                                  "frequency": "always"},
                                                 {"$type": "send_bounds",
                                                  "frequency": "always"},
                                                 {"$type": "send_image_sensors",
                                                  "frequency": "always"}]
        self.images: bool = images
        if images:
            self._next_frame_commands.append({"$type": "send_images",
                                              "frequency": "always"})
        if pass_masks is None:
            pass_masks = ["_img"]
        self._next_frame_commands.append({"$type": "set_pass_masks",
                                          "pass_masks": pass_masks,
                                          "avatar_id": self.avatar_id})
        # A command to follow a target object.
        self._follow_command: Optional[dict] = None
        Camera.RENDER_ORDER += 1
        self.move_target: MoveTarget = MoveTarget(avatar_id=self.avatar_id,
                                                  target=TDWUtils.VECTOR3_ZERO)
        self.rotate_target: RotateTarget = RotateTarget(resp=[],
                                                        avatar_id=self.avatar_id,
                                                        target={"x": 0, "y": 0, "z": 0, "w": 1})
        self.focus_target: FocusTarget = FocusTarget(avatar_id=avatar_id,
                                                     target=2,
                                                     is_object=False)

    def enable(self, enable: bool) -> None:
        """
        Enable or disable the camera.

        :param enable: If True, enable the camera.
        """

        self._next_frame_commands.append({"$type": "enable_image_sensor",
                                          "enable": enable,
                                          "avatar_id": self.avatar_id})

    def follow(self, target: Optional[int], position: Dict[str, float], rotation: bool) -> None:
        """
        Follow a target object.

        :param target: If None, stop following the object (if any). Otherwise, this is the ID of the target object.
        :param position: The position relative to the target object.
        :param rotation: If True, set the avatar's rotation to match the object's rotation.
        """

        if target is None:
            self._follow_command = None
        else:
            self._follow_command = {"$type": "follow_object",
                                    "object_id": target,
                                    "position": position,
                                    "rotation": rotation,
                                    "avatar_id": self.avatar_id}

    def get_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The most recent response from the build.

        :return: A list of commands to send to the build.
        """

        commands = self._next_frame_commands[:]
        # Either follow an object or move the camera.
        if self._follow_command is not None:
            commands.append(self._follow_command)
        else:
            commands.extend(self.move_target.get_commands(resp=resp))
        commands.extend(self.rotate_target.get_commands(resp=resp))
        commands.extend(self.focus_target.get_commands(resp=resp))
        self._next_frame_commands.clear()
        return commands
