from typing import List, Dict
from abc import ABC, abstractmethod
import numpy as np
from tdw.add_ons.model_verifier.model_tests.model_test import ModelTest
from tdw.librarian import ModelRecord
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images


class RotateObjectTest(ModelTest, ABC):
    """
    These tests add an object and then rotate it.
    """

    """:class_var
    The ID of the object.
    """
    OBJECT_ID: int = 0
    """:class_var
    Rotate by this many degrees per frame.
    """
    DELTA_THETA: int = 15
    """:class_var
    The Unity pink color.
    """
    PINK: tuple = (255, 0, 255)
    """:class_var
    Look at this position.
    """
    LOOK_AT: Dict[str, float] = {"x": 0, "y": 0.5, "z": 0}
    """:class_var
    The position of the avatar.
    """
    AVATAR_POSITION: Dict[str, float] = {"x": 1.75, "y": 0.5, "z": 0}

    def __init__(self, record: ModelRecord):
        """
        :param record: The model record.
        """

        super().__init__(record=record)
        self._axis: str = "yaw"
        self._angle: int = 0

    def start(self) -> List[dict]:
        """
        :return: A list of commands to start the test.
        """

        scale = TDWUtils.get_unit_scale(self._record)
        # Create the scene. Add the avatar. Add the object.
        return [{"$type": "send_images",
                "frequency": "always"},
                {"$type": "add_object",
                 "name": self._record.name,
                 "url": self._record.get_url(),
                 "position": {"x": 0, "y": 0, "z": 0},
                 "scale_factor": self._record.scale_factor,
                 "id": RotateObjectTest.OBJECT_ID},
                {"$type": "scale_object",
                 "id": RotateObjectTest.OBJECT_ID,
                 "scale_factor": {"x": scale, "y": scale, "z": scale}}]

    def on_send(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The response from the build.

        :return: A list of commands to continue or end the test.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imag":
                self._read_images(Images(resp[i]))
                break
        # Reading the images can cause the test to finish early.
        if self.done:
            return []
        # Either end the test or reset the angle and start rotating around a new axis.
        elif self._angle >= 360:
            if self._axis == "yaw":
                self._axis = "roll"
                self._angle = 0
                return [{"$type": "teleport_avatar_to",
                         "position": RotateObjectTest.AVATAR_POSITION},
                        {"$type": "look_at_position",
                         "position": RotateObjectTest.LOOK_AT},]
            else:
                self.done = True
                return []
        # Continue to rotate.
        else:
            self._angle += RotateObjectTest.DELTA_THETA
            rad = np.radians(self._angle)
            if self._axis == "yaw":
                x = np.cos(rad) * RotateObjectTest.AVATAR_POSITION["x"] - np.sin(rad) * RotateObjectTest.AVATAR_POSITION["z"]
                y = RotateObjectTest.AVATAR_POSITION["y"]
                z = np.sin(rad) * RotateObjectTest.AVATAR_POSITION["x"] + np.cos(rad) * RotateObjectTest.AVATAR_POSITION["z"]
            else:
                x = np.cos(rad) * RotateObjectTest.AVATAR_POSITION["x"] - np.sin(rad) * RotateObjectTest.AVATAR_POSITION["z"]
                y = (np.sin(rad) * RotateObjectTest.AVATAR_POSITION["x"] + np.cos(rad) * RotateObjectTest.AVATAR_POSITION["z"]) + RotateObjectTest.AVATAR_POSITION["y"]
                z = RotateObjectTest.AVATAR_POSITION["z"]

            return [{"$type": "teleport_avatar_to",
                     "position": {"x": x, "y": y, "z": z}},
                    {"$type": "look_at_position",
                     "position": RotateObjectTest.LOOK_AT}]

    @abstractmethod
    def _read_images(self, images: Images) -> None:
        """
        Read image data.

        :param images: The image data.
        """

        raise Exception()

    @staticmethod
    def _get_end_commands() -> List[dict]:
        """
        :return: A list of commands to end to test.
        """

        return [{"$type": "destroy_object",
                 "id": RotateObjectTest.OBJECT_ID},
                {"$type": "unload_asset_bundles"}]
