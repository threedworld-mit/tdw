from typing import List, Union
from pathlib import Path
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images


class ImageCapture(AddOn):
    """
    Per frame, request image data and save the images to disk.

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.third_person_camera import ThirdPersonCamera
    from tdw.add_ons.image_capture import ImageCapture

    c = Controller(launch_build=False)
    c.start()

    # Add a third-person camera. It will look at object 0.
        object_id = 0
    camera = ThirdPersonCamera(position={"x": 0.5, "y": 1.5, "z": -2},
                               look_at=0,
                               pass_masks=["_img", "_id"])
    # Tell the camera to capture images per-frame.
    capture = ImageCapture(avatar_ids=[camera.avatar_id], path="D:/image_capture_test")
    c.add_ons.extend([camera, capture])

    # Create an empty room and add an object.
    # The camera will be added after creating the empty room and the object.
    # The image capture add-on will initialize after the camera and save an `_img` pass and `_id` pass to disk.
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object(model_name="iron_box",
                                    object_id=object_id)])

    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, path: Union[str, Path], avatar_ids: List[str] = None, png: bool = False):
        """
        :param path: The path to the output directory.
        :param avatar_ids: The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images.
        :param png: If True, images will be lossless png files. If False, images will be jpgs. Usually, jpg is sufficient.
        """

        super().__init__()
        self._frame: int = 0
        if isinstance(path, str):
            """:field
            The path to the output directory.
            """
            self.path: Path = Path(path)
        else:
            self.path: Path = path
        if not self.path.exists():
            self.path.mkdir(parents=True)
        if avatar_ids is None:
            """:field
            The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images.
            """
            self.avatar_ids: List[str] = []
        else:
            self.avatar_ids: List[str] = avatar_ids
        self._png: bool = png

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "set_img_pass_encoding",
                 "value": self._png}]

    def on_send(self, resp: List[bytes]) -> None:
        self.commands.append({"$type": "send_images",
                              "frequency": "once",
                              "ids": self.avatar_ids})
        got_images = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imag":
                images = Images(resp[i])
                a = images.get_avatar_id()
                if len(self.avatar_ids) == 0 or a in self.avatar_ids:
                    output_dir = self.path.joinpath(a)
                    if not output_dir.exists():
                        output_dir.mkdir(parents=True)
                    # Save images.
                    TDWUtils.save_images(images=images,
                                         output_directory=str(output_dir.resolve()),
                                         filename=TDWUtils.zero_padding(self._frame, 4))
                    got_images = True
        if got_images:
            self._frame += 1
