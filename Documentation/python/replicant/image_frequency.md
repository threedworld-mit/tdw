# ImageFrequency

`from tdw.replicant.image_frequency import ImageFrequency`

The per-frame frequency of image capture.

| Value | Description |
| --- | --- |
| `once` | Capture an image only on this `communicate()` call. |
| `always` | Capture images on every `communicate()` call. |
| `never` | Don't capture images on any `communicate()` call. |