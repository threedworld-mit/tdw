from typing import List
from io import BytesIO
from PIL import Image
from collections import Counter
from tdw.add_ons.model_verifier.model_tests.rotate_object_test import RotateObjectTest
from tdw.output_data import Images
from tdw.librarian import ModelRecord


class PhysicsQuality(RotateObjectTest):
    """
    Test the "physics quality" i.e. the disparity between the colliders volume and the rendered volume.
    """

    MASK_RED = (255, 0, 0)

    def __init__(self, record: ModelRecord):
        super().__init__(record=record)
        self._showing_collider_hulls: bool = False
        self._without_collider_hulls: List[int] = list()
        self._with_collider_hulls: List[int] = list()

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
                        physics_quality = 0
                    else:
                        physics_quality = 1 - float(without_colliders - with_colliders) / without_colliders
                    qualities.append(physics_quality)
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
                return [{"$type": "show_collider_hulls",
                         "id": RotateObjectTest.OBJECT_ID},
                        {"$type": "set_pass_masks",
                         "pass_masks": ["_img"]},
                        {"$type": "rotate_object_to",
                         "rotation": {"w": 1, "x": 0, "y": 0, "z": 0},
                         "id": RotateObjectTest.OBJECT_ID},
                        {"$type": "teleport_object",
                         "id": RotateObjectTest.OBJECT_ID,
                         "position": {"x": 0, "y": 0.5, "z": 0}}]
        else:
            return commands

    def _read_images(self, images: Images) -> None:
        image = Image.open(BytesIO(images.get_image(0)))
        if self._showing_collider_hulls:
            self._with_collider_hulls.append(Counter(image.getdata())[RotateObjectTest.PINK])
        else:
            self._without_collider_hulls.append(Counter(image.getdata())[PhysicsQuality.MASK_RED])
