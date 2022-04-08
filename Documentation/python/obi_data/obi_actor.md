# ObiActor

`from tdw.obi_data.obi_actor import ObiActor`

Data for an Obi actor.

***

## Fields

- `object_id` The object ID.

- `positions` The positions of each particle as a numpy array.

- `velocities` The velocities of each particle as a numpy array.

***

## Functions

#### \_\_init\_\_

**`ObiActor(object_id, solver_id, object_index)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The object ID. |
| solver_id |  int |  | The ID of the object's Obi solver. |
| object_index |  int |  | The index of the object in the `ObiParticles` output data. |

#### on_communicate

**`self.on_communicate(obi_particles)`**

On `communicate()`, update `self.positions` and `self.velocities`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| obi_particles |  ObiParticles |  | `ObiParticles` output data. |

