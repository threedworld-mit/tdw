# ModelTest

`from tdw.add_ons.model_verifier.model_tests.model_test import ModelTest`

Run a test on a model.

***

## Fields

- `reports` A list of report strings after running the test.

- `done` If True, the test is done.

***

## Functions

#### \_\_init\_\_

**`ModelTest(record)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record |  ModelRecord |  | The model record. |

#### start

**`self.start()`**

_Returns:_  A list of commands to start the test.

#### on_send

**`self.on_send(resp)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

_Returns:_  A list of commands to continue or end the test.

