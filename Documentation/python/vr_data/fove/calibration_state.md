# CalibrationState

`from tdw.vr_data.fove.calibration_state import CalibrationState`

State machine flags for controlling FOVE calibration.

| Value | Description |
| --- | --- |
| `calibrating` | The headset is running the built-in FOVE calibration. |
| `calibrating_with_spheres` | The simulation is running a TDW-specific calibration scene. |
| `running` | The headset is done calibrating. |