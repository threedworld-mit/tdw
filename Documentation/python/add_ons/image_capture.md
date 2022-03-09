# ImageCapture

`from tdw.add_ons.image_capture import ImageCapture`

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

***

## Fields

- `frame` The current frame count. This is used to generate filenames.

- `path` The path to the output directory.

- `avatar_ids` The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images.

- `images` Raw [`Images` output data](../../api/output_data.md#Images) from the build. Key = The ID of the avatar. This is updated per frame. If an avatar didn't capture an image on this frame, it won't be in this dictionary.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ImageCapture(path)`**

**`ImageCapture(path, avatar_ids=None, png=False, pass_masks=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path] |  | The path to the output directory. |
| avatar_ids |  List[str] | None | The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images. Note that these avatars must already exist in the scene (if you've added the avatars via a [`ThirdPersonCamera` add-on](third_person_camera.md), you must add the `ThirdPersonCamera` first, *then* `ImageCapture`). |
| png |  bool  | False | If True, images will be lossless png files. If False, images will be jpgs. Usually, jpg is sufficient. |
| pass_masks |  List[str] | None | A list of image passes that will be captured by the avatars. If None, defaults to `["_img"]`. For a description of each of pass mask, [read this](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_pass_masks). |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### set

**`self.set()`**

**`self.set(frequency="always", avatar_ids=None, pass_masks=None, save=True)`**

Set the frequency of images and which avatars will capture images.
By default, all of the avatars specified in the constructor (if None, all avatars in the scene) will capture images every frame.
This function will override the previous image capture settings; in other words, setting `frequency` to `"once"` for one avatar will make all other avatars stop capturing images per frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| frequency |  str  | "always" | The frequency at which images are captured. Options: `"always"` (capture images every frame), `"once"` (capture an image only on the next frame), `"never"` (stop capturing images). |
| avatar_ids |  List[str] | None | The IDs of the avatar that will capture images. If None, all avatars in the scene will capture images. |
| pass_masks |  List[str] | None | A list of image passes that will be captured by the avatars. If None, defaults to `["_img"]`. For a description of each of pass mask, [read this](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_pass_masks). |
| save |  bool  | True | If True, automatically save images to disk per frame. If False, images won't be saved but the `self.images` dictionary will still be updated. |

#### get_pil_images

**`self.get_pil_images()`**

Convert the latest image data from the build (`self.images`) to PIL images. Note that it is not necessary to call this function to save images; use this only to analyze an image at runtime.

_Returns:_  A dictionary of PIL images from the latest image data from the build. Key = The avatar ID. Value = A dictionary; key = the pass mask, value = the PIL image.