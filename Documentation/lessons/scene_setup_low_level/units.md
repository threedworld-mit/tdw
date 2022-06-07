##### Scene Setup (Low-Level APIs)

# Units and data formats

## Units

- Distance is always in meters.
- Rotation is always in degrees.
- Velocity is always in meters per second.
- Angular velocity is always in degrees per second.
- Force is always in Newtons.
- For directional vectors such as positions and forces:
  - Positive x is to the right.
  - Positive y is up.
  - Positive z is forward.

## Data formats: Command API

| Type                                       | Format                                                       | Example                              |
| ------------------------------------------ | ------------------------------------------------------------ | ------------------------------------ |
| Directional vector (position, force, etc.) | An (x, y, z) dictionary.                                     | `{"x": 0.1, "y": 0, "z": -2}`        |
| Euler angles                               | An (x, y, z) dictionary.                                     | `{"x": 20, "y": -5, "z": 0}`         |
| Quaternion                                 | An (x, y, z, w) dictionary.                                  | `{"x": 0, "y": 0, "z": 0, "w": 1}`   |
| Color                                      | An (r, g, b, a) dictionary where each value is a float between 0 and 1. | `{"r": 1, "b": 0.2, "g": 0, "a": 1}` |

## Data formats: Output Data

| Type                                       | Format                                                       | Example        |
| ------------------------------------------ | ------------------------------------------------------------ | -------------- |
| Directional vector (position, force, etc.) | An (x, y, z) tuple                                           | `(0.1, 0, -2)` |
| Euler angles                               | An (x, y, z) tuple                                           | `(20, -5, 0)`  |
| Quaternion                                 | An (x, y, z, w) tuple                                        | `(0, 0, 0, 1)` |
| Color                                      | An (r, g, b) tuple where each element is a byte value between 0 and 255 | `(255, 0, 34)` |

## Useful wrapper functions in `TDWUtils`

| Wrapper function            | Result                                               |
| --------------------------- | ---------------------------------------------------- |
| `vector3_to_array(vector3)` | Convert an (x, y, z) dictionary to a numpy array.    |
| `array_to_vector3(arr)`     | Convert an [x, y, z] numpy array to a dictionary.    |
| `vector4_to_array(vector4)` | Convert an (x, y, z, w) dictionary to a numpy  array |
| `array_to_vector4(arr)`     | Convert an [x, y, z, w] numpy array to a dictionary. |
| `color_to_array(color`)     | Convert an (r, g, b, a) dictionary to a numpy array. |
| `array_to_color(arr)`       | Convert an [r, g, b, a] numpy array to a dictionary. |

***

**Next: [`Bounds` output data](bounds.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`TDWUtils`](../../python/tdw_utils.md)
