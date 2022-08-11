# ModelReport

`from tdw.add_ons.model_verifier.model_tests.model_report import ModelReport`

Send `send_model_report` and get a basic report on the model.

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

