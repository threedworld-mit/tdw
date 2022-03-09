# PhysicsQuality

`from tdw.add_ons.model_verifier.model_tests.physics_quality import PhysicsQuality`

Test the "physics quality" i.e. the disparity between the colliders volume and the rendered volume.

***

## Functions

#### \_\_init\_\_

**`PhysicsQuality()`**

#### start

**`self.start()`**

_Returns:_  A list of commands to start the test.

#### on_send

**`self.on_send(resp)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

_Returns:_  A list of commands to continue or end the test.

