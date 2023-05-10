from abc import ABC
from typing import List, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Framerate, Bounds
from tdw.drone.drone_dynamic import DroneDynamic
from tdw.drone.action_status import ActionStatus
from tdw.drone.image_frequency import ImageFrequency


class Action(ABC):
    """
    An action that the drone can do. An action is first initialized, has an ongoing state, and an end state.
    An action also has a status indicating whether it's ongoing, succeeded, or failed; and if it failed, why.
    """

    def __init__(self):
        """
        (no parameters)
        """

        """:field
        [The current status of the action.](../action_status.md) By default, this is `ongoing` (the action isn't done).
        """
        self.status: ActionStatus = ActionStatus.ongoing
        """:field
        If True, the action has initialized. If False, the action will try to send `get_initialization_commands(resp)` on this frame.
        """
        self.initialized: bool = False
        """:field
        If True, this action is done and won't send any more commands.
        """
        self.done: bool = False

    def get_initialization_commands(self, resp: List[bytes], dynamic: DroneDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param dynamic: The [`droneDynamic`](../drone_dynamic.md) data that changes per `communicate()` call.
        :param image_frequency: An [`ImageFrequency`](../image_frequency.md) value describing how often image data will be captured.

        :return: A list of commands to initialize this action.
        """

        commands = []
        # If we only want images at the start of the action or never, disable the camera now.
        if image_frequency == ImageFrequency.once or image_frequency == ImageFrequency.never:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": False,
                              "avatar_id": dynamic.avatar_id}])
        # If we want images per frame, enable image capture now.
        elif image_frequency == ImageFrequency.always:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": True,
                              "avatar_id": dynamic.avatar_id},
                             {"$type": "send_images",
                              "frequency": "always"},
                             {"$type": "send_camera_matrices",
                              "frequency": "always"}])
        else:
            raise Exception(f"Invalid image capture option: {image_frequency}")
        return commands

    def get_ongoing_commands(self, resp: List[bytes], dynamic: DroneDynamic) -> List[dict]:
        """
        Evaluate an action per-frame to determine whether it's done.

        :param resp: The response from the build.
        :param dynamic: The [`droneDynamic`](../drone_dynamic.md) data that changes per `communicate()` call.

        :return: A list of commands to send to the build to continue the action.
        """

        return []

    def get_end_commands(self, resp: List[bytes], dynamic: DroneDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param dynamic: The [`droneDynamic`](../drone_dynamic.md) data that changes per `communicate()` call.
        :param image_frequency: An [`ImageFrequency`](../image_frequency.md) value describing how often image data will be captured.

        :return: A list of commands that must be sent to end any action.
        """

        commands: List[dict] = []
        # Enable image capture on this frame only.
        if image_frequency == ImageFrequency.once:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": True,
                              "avatar_id": dynamic.avatar_id},
                             {"$type": "send_images",
                              "frequency": "once"},
                             {"$type": "send_camera_matrices",
                              "frequency": "once"}])
        return commands
