from abc import ABC
from typing import List, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Framerate, Bounds
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency


class Action(ABC):
    """
    An action that the Replicant can do. An action is first initialized, has an ongoing state, and an end state.
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

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param image_frequency: An [`ImageFrequency`](../image_frequency.md) value describing how often image data will be captured.

        :return: A list of commands to initialize this action.
        """

        commands = [{"$type": "replicant_step",
                     "id": static.replicant_id}]
        if static.can_walk:
            commands.append({"$type": "stop_replicant_animation",
                             "id": static.replicant_id})
        # If we only want images at the start of the action or never, disable the camera now.
        if image_frequency == ImageFrequency.once or image_frequency == ImageFrequency.never:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": False,
                              "avatar_id": static.avatar_id}])
        # If we want images per frame, enable image capture now.
        elif image_frequency == ImageFrequency.always:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": True,
                              "avatar_id": static.avatar_id},
                             {"$type": "send_images",
                              "frequency": "always"},
                             {"$type": "send_camera_matrices",
                              "frequency": "always"}])
        else:
            raise Exception(f"Invalid image capture option: {image_frequency}")
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        """
        Evaluate an action per-frame to determine whether it's done.

        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.

        :return: A list of commands to send to the build to continue the action.
        """

        return [{"$type": "replicant_step",
                 "id": static.replicant_id}]

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param image_frequency: An [`ImageFrequency`](../image_frequency.md) value describing how often image data will be captured.

        :return: A list of commands that must be sent to end any action.
        """

        commands: List[dict] = [{"$type": "replicant_step",
                                 "id": static.replicant_id}]
        # Enable image capture on this frame only.
        if image_frequency == ImageFrequency.once:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": True,
                              "avatar_id": static.avatar_id},
                             {"$type": "send_images",
                              "frequency": "once"},
                             {"$type": "send_camera_matrices",
                              "frequency": "once"}])
        return commands

    @staticmethod
    def _get_object_position(object_id: int, resp: List[bytes]) -> np.ndarray:
        """
        :param object_id: The object ID.
        :param resp: The response from the build.

        :return: The position of the object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == object_id:
                        return transforms.get_position(j)
        raise Exception(f"Transform data not found for: {object_id}")

    @staticmethod
    def _get_object_bounds(object_id: int, resp: List[bytes]) -> Dict[str, np.ndarray]:
        """
        :param object_id: The object ID.
        :param resp: The response from the build.

        :return: The bounds of the object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "boun":
                bounds = Bounds(resp[i])
                for j in range(bounds.get_num()):
                    if bounds.get_id(j) == object_id:
                        return TDWUtils.get_bounds_dict(bounds, j)
        raise Exception(f"Bounds data not found for: {object_id}")

    @staticmethod
    def _get_scaled_duration(duration: float, resp: List[bytes]) -> float:
        """
        Scale the duration by the framerate.

        :param duration: The duration of the action in seconds.
        :param resp: The response from the build.

        :return: The scaled duration.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "fram":
                framerate = 1 / Framerate(resp[i]).get_frame_dt()
                if framerate >= 60:
                    return duration * (60 / framerate)
                else:
                    return duration
        raise Exception("Framerate output data not found")
