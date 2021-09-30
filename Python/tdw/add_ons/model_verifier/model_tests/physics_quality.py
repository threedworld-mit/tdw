from typing import List
from io import BytesIO
from PIL import Image
import numpy as np
from tdw.add_ons.model_verifier.model_tests.rotate_object_test import RotateObjectTest
from tdw.output_data import Images
from tdw.librarian import ModelRecord


class PhysicsQuality(RotateObjectTest):
    """
    Test the "physics quality" i.e. the disparity between the colliders volume and the rendered volume.
    """

    def __init__(self, record: ModelRecord):
        super().__init__(record=record)
        self._showing_collider_hulls: bool = False
        self._without_collider_hulls: List[float] = list()
        self._with_collider_hulls: List[float] = list()

    def start(self) -> List[dict]:
        """
        :return: A list of commands to start the test.
        """

        commands = super().start()
        commands.insert(0, {"$type": "set_pass_masks",
                            "pass_masks": ["_mask"]})
        return commands

    def on_send(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The response from the build.

        :return: A list of commands to continue or end the test.
        """

        commands = super().on_send(resp=resp)
        if self.done:
            # Done with both passes. Get the physics quality.
            if self._showing_collider_hulls:
                qualities: List[float] = list()
                for with_colliders, without_colliders in zip(self._with_collider_hulls, self._without_collider_hulls):
                    if without_colliders == 0:
                        qualities.append(0)
                    else:
                        qualities.append(1 - (float(with_colliders) / float(without_colliders)))
                if len(qualities) == 0:
                    physics_quality = -1
                else:
                    physics_quality = float(sum(qualities)) / len(qualities)
                self.reports.append(str(physics_quality))
                commands.extend(RotateObjectTest._get_end_commands())
                return commands
            # Show the colliders and start rotating again.
            else:
                self._showing_collider_hulls = True
                self.done = False
                self._angle = 0
                self._axis = "yaw"
                commands = [{"$type": "show_collider_hulls",
                             "id": RotateObjectTest.OBJECT_ID}]
                commands.extend(super().on_send(resp=resp))
                return commands
        else:
            return commands

    def _read_images(self, images: Images) -> None:
        image = np.array(Image.open(BytesIO(images.get_image(0))))
        quality = (256 * 256) - np.sum(np.all(image == np.array([0, 0, 0]), axis=2))
        if self._showing_collider_hulls:
            self._with_collider_hulls.append(quality)
        else:
            self._without_collider_hulls.append(quality)
