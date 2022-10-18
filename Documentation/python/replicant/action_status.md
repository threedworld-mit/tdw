# ActionStatus

`from tdw.replicant.action_status import ActionStatus`

The status of the Replicant after doing an action.

| Value | Description |
| --- | --- |
| `ongoing` | The action is ongoing. |
| `failure` | Generic failure code (useful for custom APIs). |
| `success` | The action was successful. |
| `failed_to_move` | Tried to move to a target position or object but failed. |
| `failed_to_turn` | Tried to turn but failed to align with the target angle, position, or object. |
| `cannot_reach` | Didn't try to reach for the target position because it can't. |
| `failed_to_reach` | Tried to reach for the target but failed; the magnet isn't close to the target. |
| `not_holding` | Didn't try to drop the object(s) because it isn't holding them. |
| `collision` | Tried to move or turn but failed because it collided with something. |
| `detected_obstacle` | Detected an obstacle in its path. |
| `already_holding` | Already holding the object. |
| `still_dropping` | Dropped an object but, after many `communicate()` calls, the object is still moving. |