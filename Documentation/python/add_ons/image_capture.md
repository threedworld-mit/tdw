# ImageCapture

`from tdw.add_ons.image_capture import ImageCapture`

Per frame, request image data and save the images to disk.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `path` The path to the output directory.

- `avatar_ids` The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images.

***

## Functions

#### \_\_init\_\_

**`ImageCapture(path)`**

**`ImageCapture(path, avatar_ids=None, png=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path] |  | The path to the output directory. |
| avatar_ids |  List[str] | None | The IDs of the avatars that will capture and save images. If empty, all avatars will capture and save images. |
| png |  bool  | False | If True, images will be lossless png files. If False, images will be jpgs. Usually, jpg is sufficient. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

_Returns:_  A list of commands that will initialize this module.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

##### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |



