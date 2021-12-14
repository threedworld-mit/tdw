# AssetBundleCreatorBase

`from tdw.asset_bundle_creator_base import AssetBundleCreatorBase`

Base class for creating asset bundles.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `UNITY_VERSION` | str | Use this version of Unity Editor to launch the asset bundle creator. |

***

## Functions

#### \_\_init\_\_

**`AssetBundleCreatorBase()`**

**`AssetBundleCreatorBase(quiet=False, display="0")`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If true, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |

#### get_base_unity_call

**`self.get_base_unity_call()`**

_Returns:_  The call to launch Unity Editor silently in batchmode, execute something, and then quit.

#### get_editor_path

**`AssetBundleCreatorBase(ABC).get_editor_path()`**

_This is a static function._

Build the asset_bundle_creator Unity project.

_Returns:_  The path to the asset_bundle_creator Unity project.

#### get_unity_project

_(Abstract)_

**`self.get_unity_project()`**

Build the asset_bundle_creator Unity project.

_Returns:_  The path to the asset_bundle_creator Unity project.

#### get_project_path

_(Abstract)_

**`self.get_project_path()`**

_Returns:_  The expected path of the Unity project.

