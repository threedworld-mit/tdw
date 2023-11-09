# VRayExporter

`from tdw.add_ons.vray_exporter import VRayExporter`

Render TDW scenes offline using V-Ray for enhanced photorealism.

This add-on converts scene-state data in TDW per communicate() call and saves it as .vrscene data, which can then be rendered with Chaos Vantage.

Rendering is typically done after the scene or trial is done, via `self.launch_renderer(output_directory)`. The renderer can be a local or remote executable.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `S3_ROOT` | str | The S3 URL root. | `"https://tdw-public.s3.amazonaws.com/"` |
| `VRAY_EXPORT_RESOURCES_PATH` | Path | The path to location of all downloaded and exported .vrscene files, maps etc. | `Path.home().joinpath("vray_export_resources")` |

***

## Fields

- `vray_model_list` The list of each model that can be rendered with VRay. The first time you run this add-on, it will query the S3 server for a list of models and save the result to `~/vray_export_resources/models.txt`, which it will use for all subsequent runs.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`VRayExporter(image_width, image_height, scene_name)`**

**`VRayExporter(image_width, image_height, scene_name, animate=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| image_width |  int |  | The image width in pixels. |
| image_height |  int |  | The image height in pixels. |
| scene_name |  str |  | The scene name. This must match the scene being used in the TDW build, e.g. `"tdw_room"`. |
| animate |  bool  | False | If True, render an animation of each frame. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### launch_renderer

**`self.launch_renderer(output_directory)`**

**`self.launch_renderer(output_directory, render_host="localhost", port=1204, renderer_path="C/Program Files/Chaos Group/Vantage/vantage_console.exe")`**

Launch Vantage in headless mode and render scene file, updating for animation if necessary.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| output_directory |  Union[str, Path] |  | The root output directory. If `render_host == "localhost"`, this directory will be created if it doesn't already exist. On a remote server, the directory must already exist. |
| render_host |  str  | "localhost" | The render host IP address. |
| port |  int  | 1204 | The socket port for the render host. This is only used for remote SSHing. |
| renderer_path |  str  | "C/Program Files/Chaos Group/Vantage/vantage_console.exe" | The file path to the Vantage console executable. |