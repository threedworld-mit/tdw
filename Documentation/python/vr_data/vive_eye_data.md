# ViveEyeData

`from tdw.vr_data.vive_eye_data import ViveEyeData`

Vive eye-tracking data.

***

## Fields

- `valid` If True, there is valid eye tracking data.

- `ray` A numpy array describing the eye ray. Shape: `(2, 3)`. Order: `(origin, direction)`. This is only valid data is `valid == True`.

- `blinking` A numpy array of booleans describing whether each eye is blinking: `[left, right]`. This is only valid data is `valid == True`.

***

## Functions

#### \_\_init\_\_

**`ViveEyeData(valid, ray, blinking)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| valid |  bool |  | If True, there is valid eye tracking data. |
| ray |  np.ndarray |  | A numpy array describing the eye ray. Shape: `(2, 3)`. Order: `(origin, direction)`. This is only valid data is `valid == True`. |
| blinking |  np.ndarray |  | A numpy array of booleans describing whether each eye is blinking: `[left, right]`. This is only valid data is `valid == True`. |

#### get_default_data

**`self.get_default_data()`**

_Returns:_  Default `ViveEyeData`.

