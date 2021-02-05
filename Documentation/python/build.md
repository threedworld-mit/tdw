# `release/build.py`

## `Build`

`from tdw.release.build import Build`

Various helper functions for TDW builds.

***

#### `get_url(version: str = __version__) -> Tuple[str, bool]`

_This is a static function._


| Parameter | Description |
| --- | --- |
| version | The version of the build. Default = the installed version of TDW. |

_Returns:_  The URL of the build release matching the version and the OS of this machine, True if the URL exists.

***

#### `download(version: str = __version__, v_prefix: bool = True) -> bool`

_This is a static function._

Download the release corresponding to this version. Move it to the build path and extract it.

| Parameter | Description |
| --- | --- |
| version | The version of the build. Default = the installed version of TDW. |
| v_prefix | If True, add a `v` to the start of the `version` string. |

_Returns:_  True if the build downloaded.

***

