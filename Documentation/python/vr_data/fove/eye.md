# Eye

`from tdw.vr_data.fove.eye import Eye`

FOVE eye data.

***

## Fields

- `state` The state of the eye: not_connected, opened, or closed.

- `direction` Where the eye is looking.

- `gaze_id` The ID of the object that the eye is gazing at. Can be None.

- `gaze_position` The position hit by the eye's ray. The ray can hit either an object or a scene mesh. Can be None.

***

## Functions

#### \_\_init\_\_

**`Eye(state, direction, gaze_id, gaze_position)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| state |  EyeState |  | The state of the eye: not_connected, opened, or closed. |
| direction |  np.ndarray |  | Where the eye is looking. |
| gaze_id |  Optional[int] |  | The ID of the object that the eye is gazing at. Can be None. |
| gaze_position |  Optional[np.ndarray] |  | The position hit by the eye's ray. The ray can hit either an object or a scene mesh. Can be None. |

