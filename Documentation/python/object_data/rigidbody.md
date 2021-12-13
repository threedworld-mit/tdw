# Rigidbody

`from tdw.object_data.rigidbody import Rigidbody`

Dynamic object rigidbody data. Note that this excludes *static* rigidbody data such as the mass of the object.

***

## Fields

- `velocity` The directional velocity of the object.

- `angular_velocity` The angular velocity of the object.

- `sleeping` If True, the object isn't moving.

***

## Functions

#### \_\_init\_\_

**`Rigidbody(velocity, angular_velocity, sleeping)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| velocity |  np.array |  | The directional velocity of the object. |
| angular_velocity |  np.array |  | The angular velocity of the object. |
| sleeping |  bool |  | If True, the object isn't moving. |

