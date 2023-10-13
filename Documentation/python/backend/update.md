# Update

`from tdw.backend.update import Update`

Check for updates on PyPi. If there are any, let the user know.

Check if the build version is behind the local Python version. If so, download a new build.

***

## Functions

#### get_pypi_version

**`Update.get_pypi_version()`**

_(Static)_

_Returns:_  The latest version of TDW on PyPi.

#### check_for_update

**`Update.check_for_update(download_build)`**

_(Static)_

Get the latest version of TDW on PyPi and compare it to the locally installed version.
Tell the user to upgrade if needed.

Optionally, compare the version of the build to the locally installed Python version.
If there is a mismatch, download the build.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| download_build |  bool |  | If True, check the version of the build and download a new one if needed. |

_Returns:_  True if it is possible to launch the build.

