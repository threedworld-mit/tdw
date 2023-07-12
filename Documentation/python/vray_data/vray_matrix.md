# VRayMatrix

`from tdw.vray_data.vray_matrix import VRayMatrix`

Matrix data for a VRay object or camera.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `HANDEDNESS` | np.ndarray | Conversion matrix from Y-up to Z-up, and left-hand to right-hand. | `np.array([[-1, 0, 0, 0],` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`VRayMatrix()`**

#### get_converted_node_matrix

**`self.get_converted_node_matrix(matrix)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| matrix |  np.ndarray |  | The object transform matrix. |

_Returns:_  The converted matrix as a `VRayMatrix`.

#### get_converted_camera_matrix

**`self.get_converted_camera_matrix(avatar_matrix, sensor_matrix)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_matrix |  np.ndarray |  | The avatar transform matrix. |
| sensor_matrix |  np.ndarray |  | The sensor container matrix. |

_Returns:_  The converted matrices as a `VRayMatrix`.