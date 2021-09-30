# ModelVerifier

`from tdw.add_ons.model_verifier import ModelVerifier`

Run tests on an object model.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

- `reports` A list of reports from the test.

- `done` If True, the tests are done.

***

## Functions

#### \_\_init\_\_

**`ModelVerifier()`**

A list of reports from the test.

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### set_tests

**`self.set_tests(name, model_report, missing_materials, physics_quality)`**

**`self.set_tests(name, source=None, model_report, missing_materials, physics_quality)`**

Start new tests for the model. Only call this if there isn't currently a test running.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model. |
| source |  Union[ModelLibrarian, ModelRecord, str] | None | The source of the model. If None: Get the record corresponding to `name` in `models_core.json`. If `ModelLibrarian`: Get the record corresponding to `name` in this library. If `ModelRecord`: Use this record. If `str`: Create a dummy record with name `name` and URL `source`. |
| model_report |  bool |  | If True, run a basic test on the model. |
| missing_materials |  bool |  | If True, test the model for any missing materials. |
| physics_quality |  bool |  | If True, test the extent to which the colliders geometry matches the rendered geometry. |

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |



