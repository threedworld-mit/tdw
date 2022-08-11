# RotateObjectTest

`from tdw.add_ons.model_verifier.model_tests.rotate_object_test import RotateObjectTest`

These tests add an object and then rotate it.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `OBJECT_ID` | int | The ID of the object. | `0` |
| `DELTA_THETA` | int | Rotate by this many degrees per frame. | `15` |
| `PINK` | tuple | The Unity pink color. | `(255, 0, 255)` |
| `LOOK_AT` | Dict[str, float] | Look at this position. | `{"x": 0, "y": 0.5, "z": 0}` |
| `AVATAR_POSITION` | Dict[str, float] | The position of the avatar. | `{"x": 1.75, "y": 0.5, "z": 0}` |

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

