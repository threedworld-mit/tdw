# RemoteBuildLauncher

`from tdw.remote_build_launcher import RemoteBuildLauncher`

Connect to a remote binary_manager daemon and launch an instance of a TDW build.

***

## Functions

#### launch_build

**`RemoteBuildLauncher.launch_build(listener_port, build_address, controller_address)`**

_(Static)_

Connect to a remote binary_manager daemon and launch an instance of a TDW build.

Returns the necessary information for a local controller to connect.
Use this function to automatically launching binaries on remote (or local) nodes, and to
automatically shut down the build after controller is finished. Call in the constructor
of a controller and pass the build_port returned in build_info to the parent Controller class.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| listener_port |  int |  | The port launch_binaries is listening on. |
| build_address |  str |  | Remote IP or hostname of node running launch_binaries. |
| controller_address |  str |  | IP or hostname of node running controller. |

_Returns:_  The build_info dictionary containing build_port.

#### get_unity_args

**`RemoteBuildLauncher.get_unity_args(arg_dict)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arg_dict |  dict |  | A dictionary of arguments. Key=The argument prefix (e.g. port) Value=Argument value. |

_Returns:_  The formatted command line string that is accepted by unity arg parser.

#### find_free_port

**`RemoteBuildLauncher.find_free_port()`**

_(Static)_

_Returns:_  A free socket port.

