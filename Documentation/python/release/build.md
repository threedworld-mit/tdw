# Build

`from tdw.release.build import Build`

Various helper functions for TDW builds.

***

## Functions

#### get_url

**`Build.get_url()`**

**`Build.get_url(version=__version__, check_head=True)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| version |  str  | __version__ | The version of the build. Default = the installed version of TDW. |
| check_head |  bool  | True | If True, check the HTTP headers to make sure that the release exists. |

_Returns:_  The URL of the build release matching the version and the OS of this machine, True if the URL exists.

#### download

**`Build.download()`**

**`Build.download(version=__version__, v_prefix=True)`**

_(Static)_

Download the release corresponding to this version. Move it to the build path and extract it.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| version |  str  | __version__ | The version of the build. Default = the installed version of TDW. |
| v_prefix |  bool  | True | If True, add a `v` to the start of the `version` string. |

_Returns:_  True if the build downloaded.

