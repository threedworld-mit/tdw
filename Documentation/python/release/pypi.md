# PyPi

`from tdw.release.pypi import PyPi`

Compare the version of the installed tdw Python module to the PyPi version.

***

## Functions

#### strip_post_release

**`PyPi.strip_post_release(v)`**

_(Static)_

If the version number has a post-release suffix (a fourth number), strip it.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| v |  str |  | The version number. |

_Returns:_  The version, stripped of the post-release suffix.

#### get_major_release

**`PyPi.get_major_release(v)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| v |  str |  | The version number. |

_Returns:_  The major release number (example: in 1.7.0, the major release is 7).

#### get_pypi_version

**`PyPi.get_pypi_version()`**

**`PyPi.get_pypi_version(truncate=False)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| truncate |  bool  | False | If true, remove the post-release number (the fourth number) if there is one. |

_Returns:_  The newest available tdw release on PyPi.

#### get_installed_tdw_version

**`PyPi.get_installed_tdw_version()`**

**`PyPi.get_installed_tdw_version(truncate=False)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| truncate |  bool  | False | If true, remove the post-release number (the fourth number) if there is one. |

_Returns:_  The version of the tdw Python module installed on this machine.

#### get_latest_post_release

**`PyPi.get_latest_post_release(v)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| v |  str |  | A three-part version string, e.g. 1.6.1 |

_Returns:_  The most up-to-date version or post-release of the tdw module on PyPi with `v`, e.g. 1.6.1.10

#### get_latest_minor_release

**`PyPi.get_latest_minor_release(v)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| v |  str |  | The version number. |

_Returns:_  The most up-to-date version in this major release. (Example: if v == 1.5.0, this returns 1.5.5)

#### required_tdw_version_is_installed

**`PyPi.required_tdw_version_is_installed(required_version, build_version)`**

**`PyPi.required_tdw_version_is_installed(required_version, build_version, comparison="==")`**

_(Static)_

Check whether the correct version of TDW is installed.
This is useful for other modules such as the Magnebot API that rely on certain versions of TDW.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| required_version |  str |  | The required version of TDW. |
| build_version |  str |  | The version of the build. |
| comparison |  str  | "==" | The type of comparison. Options: "==", ">", ">=". |

_Returns:_  True if the installed tdw module is the correct version.

