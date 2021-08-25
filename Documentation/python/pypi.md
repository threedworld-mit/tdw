# `release/pypi.py`

## `PyPi`

`from tdw.release.pypi import PyPi`

Compare the version of the installed tdw Python module to the PyPi version.

***

#### `strip_post_release(v: str) -> str`

_This is a static function._

If the version number has a post-release suffix (a fourth number), strip it.

| Parameter | Description |
| --- | --- |
| v | The version number. |

_Returns:_  The version, stripped of the post-release suffix.

***

#### `get_major_release(v: str) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| v | The version number. |

_Returns:_  The major release number (example: in 1.7.0, the major release is 7).

***

#### `get_pypi_version(truncate: bool = False) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| truncate | If true, remove the post-release number (the fourth number) if there is one. |

_Returns:_  The newest available tdw release on PyPi.

***

#### `get_installed_tdw_version(truncate: bool = False) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| truncate | If true, remove the post-release number (the fourth number) if there is one. |

_Returns:_  The version of the tdw Python module installed on this machine.

***

#### `get_latest_post_release(v: str) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| v | A three-part version string, e.g. 1.6.1 |

_Returns:_  The most up-to-date version or post-release of the tdw module on PyPi with `v`, e.g. 1.6.1.10

***

#### `get_latest_minor_release(v: str) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| v | The version number. |

_Returns:_  The most up-to-date version in this major release. (Example: if v == 1.5.0, this returns 1.5.5)

***

#### `required_tdw_version_is_installed(required_version: str, build_version: str, comparison: str = "equals") -> bool`

_This is a static function._

Check whether the correct version of TDW is installed.
This is useful for other modules such as the Magnebot API that rely on certain versions of TDW.

| Parameter | Description |
| --- | --- |
| required_version | The required version of TDW. |
| build_version | The version of the build. |
| comparison | The type of comparison. Options: "equals", "greater_than", "greater_than_or_equals". |

_Returns:_  True if the installed tdw module is the correct version.

***

