# AssetBundleCreatorBase

`from tdw.asset_bundle_creator_base import AssetBundleCreatorBase`

Base class for creating asset bundles.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `UNITY_VERSION` | str | Use this version of Unity Editor to launch the asset bundle creator. | `"2020.3"` |

***

## Functions

#### \_\_init\_\_

**`AssetBundleCreatorBase()`**

**`AssetBundleCreatorBase(quiet=False, display="0", unity_editor_path=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If True, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |

#### get_base_unity_call

**`self.get_base_unity_call()`**

_Returns:_  The call to launch Unity Editor silently in batchmode, execute something, and then quit.

#### get_unity_project

**`self.get_unity_project()`**

Build the asset_bundle_creator Unity project.

_Returns:_  The path to the asset_bundle_creator Unity project.

#### get_project_path

**`self.get_project_path()`**

_Returns:_  The expected path of the Unity project.