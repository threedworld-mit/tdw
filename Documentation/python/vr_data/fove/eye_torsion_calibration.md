# EyeTorsionCalibration

`from tdw.vr_data.fove.eye_torsion_calibration import EyeTorsionCalibration`

Indicate whether each eye torsion calibration should be run.

| Value | Description |
| --- | --- |
| `default` | Use the settings coming from the configuration file. |
| `if_enabled` | Run eye torsion calibration only if the capability is currently enabled. |
| `always` | Always run eye torsion calibration independently of whether the capability is used. |