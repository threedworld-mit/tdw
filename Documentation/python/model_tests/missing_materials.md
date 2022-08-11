# MissingMaterials

`from tdw.add_ons.model_verifier.model_tests.missing_materials import MissingMaterials`

Check if any materials are missing.

***

## Functions

#### start

**`self.start()`**

_Returns:_  A list of commands to start the test.

#### on_send

**`self.on_send(resp)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

_Returns:_  A list of commands to continue or end the test.

