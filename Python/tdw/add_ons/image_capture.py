from typing import List, Union, Dict
from pathlib import Path
from PIL.Image import Image
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images


class ImageCapture(AddOn):
    """
    Request image data and save the images to disk. By default, images will be saved every frame for each specified avatar, but this add-on can be reset to save images for specific avatars, certain frames, etc.

    Note that image capture in TDW is *not* the same as image *rendering*. An avatar can render image to a display without actually sending them to the controller.
    Sending images and image passes (such as the `_id` segmentation color pass) is the slowest process in TDW; only request image capture when you actually need it.

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.third_person_camera import ThirdPersonCamera
    from tdw.add_ons.image_capture import ImageCapture

    c = Controller(launch_build=False)

    # Add a third-person camera. It will look at object 0.
    object_id = 0
    camera = ThirdPersonCamera(position={"x": 0.5, "y": 1.5, "z": -2},
                               look_at=object_id)
    # Tell the camera to capture images per-frame.
    capture = ImageCapture(avatar_ids=[camera.avatar_id], path="D:/image_capture_test", pass_masks=["_img", "_id"])
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

    # A list of valid pass masks.
    _PASS_MASKS: List[str] = list(Images.PASS_MASKS.values())

    def __init__(self, path: Union[str, Path], avatar_ids: List[str] = None, png: bool = False, pass_masks: List[str] = None):
        """
        :param path: The path to the output directory.
        :param avatar_ids: The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images. Note that these avatars must already exist in the scene (if you've added the avatars via a [`ThirdPersonCamera` add-on](third_person_camera.md), you must add the `ThirdPersonCamera` first, *then* `ImageCapture`).
        :param png: If True, images will be lossless png files. If False, images will be jpgs. Usually, jpg is sufficient.
        :param pass_masks: A list of image passes that will be captured by the avatars. If None, defaults to `["_img"]`. For a description of each of pass mask, [read this](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_pass_masks).
        """

        super().__init__()
        """:field
        The current frame count. This is used to generate filenames.
        """
        self.frame: int = 0
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
        # If True, encode the _img pass as a png.
        self._png: bool = png
        # A list of pass mask commands to send on the next frame.
        self._pass_mask_commands: List[dict] = self._get_pass_mask_commands(pass_masks=pass_masks)
        # The frequency at which images are sent.
        self._frequency: str = "always"
        # If True, save images per frame.
        self._save: bool = True

        """:field
        Raw [`Images` output data](../../api/output_data.md#Images) from the build. Key = The ID of the avatar. This is updated per frame. If an avatar didn't capture an image on this frame, it won't be in this dictionary.
        """
        self.images: Dict[str, Images] = dict()

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "set_img_pass_encoding",
                     "value": self._png}]
        # Get the pass masks.
        commands.extend(self._pass_mask_commands)
        # Begin by sending images for the next frame.
        commands.append({"$type": "send_images",
                         "frequency": "once",
                         "ids": self.avatar_ids})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        got_images = False
        self.images.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imag":
                images = Images(resp[i])
                a = images.get_avatar_id()
                # Store the image data.
                self.images[a] = images
                if self._save and (len(self.avatar_ids) == 0 or a in self.avatar_ids):
                    output_dir = self.path.joinpath(a)
                    if not output_dir.exists():
                        output_dir.mkdir(parents=True)
                    # Save images.
                    TDWUtils.save_images(images=images,
                                         output_directory=str(output_dir.resolve()),
                                         filename=TDWUtils.zero_padding(self.frame, 4))
                    got_images = True
        if got_images:
            self.frame += 1
        # If we're requesting images per-frame, send the command.
        # We can't use the "always" value because of cases like that Magnebot that will turn off image capture.
        if self._frequency == "always":
            self.commands.append({"$type": "send_images",
                                  "frequency": "once",
                                  "ids": self.avatar_ids})

    def set(self, frequency: str = "always", avatar_ids: List[str] = None, pass_masks: List[str] = None, save: bool = True) -> None:
        """
        Set the frequency of images and which avatars will capture images.
        By default, all of the avatars specified in the constructor (if None, all avatars in the scene) will capture images every frame.
        This function will override the previous image capture settings; in other words, setting `frequency` to `"once"` for one avatar will make all other avatars stop capturing images per frame.

        :param frequency: The frequency at which images are captured. Options: `"always"` (capture images every frame), `"once"` (capture an image only on the next frame), `"never"` (stop capturing images).
        :param avatar_ids: The IDs of the avatar that will capture images. If None, all avatars in the scene will capture images.
        :param pass_masks: A list of image passes that will be captured by the avatars. If None, defaults to `["_img"]`. For a description of each of pass mask, [read this](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_pass_masks).
        :param save: If True, automatically save images to disk per frame. If False, images won't be saved but the `self.images` dictionary will still be updated.
        """

        self.avatar_ids: List[str] = avatar_ids if avatar_ids is not None else []
        self._pass_mask_commands = self._get_pass_mask_commands(pass_masks=pass_masks)
        self.commands.extend(self._pass_mask_commands)
        self._save = save
        self._frequency = frequency
        if self._frequency == "always":
            # This is handled in on_send()
            pass
        # Send images once or never.
        elif self._frequency == "once" or self._frequency == "never":
            self.commands.append({"$type": "send_images",
                                  "frequency": self._frequency,
                                  "ids": self.avatar_ids})
        else:
            raise Exception(f"Invalid frequency: {self._frequency}")

    def get_pil_images(self) -> Dict[str, Dict[str, Image]]:
        """
        Convert the latest image data from the build (`self.images`) to PIL images. Note that it is not necessary to call this function to save images; use this only to analyze an image at runtime.

        :return: A dictionary of PIL images from the latest image data from the build. Key = The avatar ID. Value = A dictionary; key = the pass mask, value = the PIL image.
        """

        images: Dict[str, Dict[str, Image]] = dict()
        for avatar_id in self.images:
            images[avatar_id] = dict()
            for i in range(self.images[avatar_id].get_num_passes()):
                images[avatar_id][self.images[avatar_id].get_pass_mask(i)] = \
                    TDWUtils.get_pil_image(images=self.images[avatar_id], index=i)
        return images

    def _get_pass_mask_commands(self, pass_masks: List[str] = None) -> List[dict]:
        """
        :param pass_masks: The pass masks. If None, defaults to `["_img"]`.

        :return: A list of commands to set pass masks per avatar.
        """

        # Set the pass masks.
        if pass_masks is None:
            pass_masks = ["_img"]
        for pm in pass_masks:
            if pm not in ImageCapture._PASS_MASKS:
                raise Exception(f"Invalid pass mask: {pm}")
        return [{"$type": "set_pass_masks", "pass_masks": pass_masks, "avatar_id": a} for a in self.avatar_ids]

