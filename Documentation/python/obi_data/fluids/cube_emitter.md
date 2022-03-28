# CubeEmitter

`from tdw.obi_data.fluids.cube_emitter import CubeEmitter`

A cube-shaped Obi fluid emitter.

***

## Fields

- `size` The size of the cube in meters. If None, defaults to (0.1, 0.1, 0.1).

- `sampling_method` The [`SamplingMethod`](sampling_method).

***

## Functions

#### \_\_init\_\_

**`CubeEmitter()`**

**`CubeEmitter(size=None, sampling_method=EmitterSamplingMethod.volume)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| size |  Dict[str, float] | None | The size of the cube in meters. If None, defaults to (0.1, 0.1, 0.1). |
| sampling_method |  EmitterSamplingMethod  | EmitterSamplingMethod.volume | The [`SamplingMethod`](sampling_method). |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.