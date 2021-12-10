# Transform

`from tdw.object_data.transform import Transform`

Positional data for an object, robot body part, etc.

***

## Fields

- `position` The position vector of the object as a numpy array: `[x, y, z]` The position of each object is the bottom-center point of the object. The position of each Magnebot body part is in the exact center of the body part. `y` is the up direction.

- `rotation` The rotation quaternion of the object as a numpy array: `[x, y, z, w]` See: [`tdw.quaternion_utils.QuaternionUtils`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/tdw_utils.md#quaternionutils).

- `forward` The forward directional vector of the object as a numpy array: `[x, y, z]`

***

## Functions

#### \_\_init\_\_

**`Transform(position, rotation, forward)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  np.array |  | The position vector of the object as a numpy array. |
| rotation |  np.array |  | The rotation quaternion of the object as a numpy array. |
| forward |  np.array |  | The forward directional vector of the object as a numpy array. |

