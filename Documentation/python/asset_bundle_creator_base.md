# `asset_bundle_creator_base.py`

## `AssetBundleCreatorBase(ABC)`

`from tdw.asset_bundle_creator_base import AssetBundleCreatorBase`

Base class for creating asset bundles.

***

#### `__init__(self, quiet: bool = False, display: str = ":0")`


| Parameter | Description |
| --- | --- |
| quiet | If true, don't print any messages to console. |
| display | The display to launch Unity Editor on. Ignored if this isn't Linux. |

***

#### `get_base_unity_call(self) -> List[str]`

_Returns:_ The call to launch Unity Editor silently in batchmode, execute something, and then quit.

***

#### `get_editor_path() -> Path`

_This is a static function._

Build the asset_bundle_creator Unity project.

_Returns:_ The path to the asset_bundle_creator Unity project.

***

#### `get_unity_project(self) -> Path`

Build the asset_bundle_creator Unity project.

_Returns:_ The path to the asset_bundle_creator Unity project.

***

#### `import_unity_package(self, unity_project_path: Path) -> None`

Import the .unitypackage file into the Unity project.

| Parameter | Description |
| --- | --- |
| unity_project_path | The path to the Unity project. |

***

#### `get_project_path() -> Path`

_Returns:_  The expected path of the Unity project.

***

#### `get_unity_package() -> str`

_Returns:_  The name of the .unitypackage file.

***

