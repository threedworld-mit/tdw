# SphereEmitter

`from tdw.obi_data.fluids.sphere_emitter import SphereEmitter`

A sphere-shaped Obi fluid emitter.

***

## Fields

- `radius` The radius of the sphere.

- `sampling_method` The [`EmitterSamplingMethod`](emitter_sampling_method.md).

***

## Functions

#### \_\_init\_\_

**`SphereEmitter()`**

**`SphereEmitter(radius=0.1, sampling_method=EmitterSamplingMethod.volume)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| radius |  float  | 0.1 | The radius of the sphere. |
| sampling_method |  EmitterSamplingMethod  | EmitterSamplingMethod.volume | The [`EmitterSamplingMethod`](emitter_sampling_method.md). |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.