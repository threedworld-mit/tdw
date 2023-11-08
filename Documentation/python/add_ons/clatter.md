# Clatter

`from tdw.add_ons.clatter import Clatter`

Initialize [Clatter](../../lessons/clatter/overview.md) in TDW.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`Clatter()`**

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

#### reset

**`self.reset()`**

**`self.reset(objects=None, random_seed=None)`**

Reset Clatter.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| objects |  Dict[int, ClatterObject] | None | A dictionary of [`ClatterObject`](../physics_audio/clatter_object.md) overrides. Key = object ID. If None, the list is empty. If an object is in the scene but not in this list, TDW will try to automatically create a `ClatterObject` for it, either using pre-calculated data or by deriving parameter values. |
| random_seed |  int  | None | The random seed. If None, the seed is randomly selected within the build. |

#### get_size

**`Clatter.get_size(model)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model |  Union[np.ndarray, ModelRecord] |  | Either the extents of an object or a model record. |

_Returns:_  The `size` integer of the object.