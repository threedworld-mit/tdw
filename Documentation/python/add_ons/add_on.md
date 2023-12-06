# AddOn

`from tdw.add_ons.add_on import AddOn`

Controller add-ons can be "attached" to any controller to add functionality into the `communicate()` function.

Add-ons work by reading the response from the build and building a list of commands to be sent on the next `Controller.communicate(commands)` call.
Anything that add-ons do can be replicated elsewhere via the TDW Command API, which means that these add-ons don't provide _additional_ functionality to TDW; rather, they are utility objects for commonly required tasks such as image capture.

We recommend that new TDW users use add-ons in their controllers, while more experienced users might prefer to have more fine-grained control. Add-ons are a new feature in TDW as of v1.9.0 and we're still in the process of updating our example controllers.

To attach an add-on, append it to the `add_ons` list. Every time `Controller.communicate(commands)` is called, the add-on will evaluate the response from the build via `on_send(resp)`.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`AddOn()`**

(no parameters)

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