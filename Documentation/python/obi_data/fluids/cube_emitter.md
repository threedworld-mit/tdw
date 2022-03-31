# CubeEmitter

`from tdw.obi_data.fluids.cube_emitter import CubeEmitter`

A cube-shaped Obi fluid emitter.

***

## Fields

- `size` The size of the cube in meters. If None, defaults to `{"x": 0.1, "y": 0.1, "z": 0.1}`.

- `sampling_method` The [`EmitterSamplingMethod`](emitter_sampling_method.md).

***

## Functions

#### \_\_init\_\_

**`CubeEmitter()`**

**`CubeEmitter(size=None, sampling_method=EmitterSamplingMethod.volume)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| size |  Dict[str, float] | None | The size of the cube in meters. If None, defaults to `{"x": 0.1, "y": 0.1, "z": 0.1}`. |
| sampling_method |  EmitterSamplingMethod  | EmitterSamplingMethod.volume | The [`EmitterSamplingMethod`](emitter_sampling_method.md). |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.