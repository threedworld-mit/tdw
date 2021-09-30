# RotateObjectTest

`from model_tests.rotate_object_test import RotateObjectTest`

These tests add an object and then rotate it.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `OBJECT_ID` | int | The ID of the object. |
| `DELTA_THETA` | int | Rotate by this many degrees per frame. |

***

## Functions

#### \_\_init\_\_

**`RotateObjectTest(record)`**

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

