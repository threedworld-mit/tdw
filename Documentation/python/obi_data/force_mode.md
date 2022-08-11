# ForceMode

`from tdw.obi_data.force_mode import ForceMode`

Force modes for Obi actors.

| Value | Description |
| --- | --- |
| `force` | Add a continuous force to the object, using its mass. |
| `impulse` | Add an instant force impulse to the object, using its mass. |
| `velocity_change` | Add an instant velocity change to the object, ignoring its mass. |
| `acceleration` | Add a continuous acceleration to the object, ignoring its mass. |