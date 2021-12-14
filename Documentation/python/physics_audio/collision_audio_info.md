# CollisionAudioInfo

`from tdw.physics_audio.collision_audio_info import CollisionAudioInfo`

Class containing information about collisions required by PyImpact to determine the volume of impact sounds.

***

## Fields

- `count` The collision counter.

- `amp` Amplitude of the first collision (must be between 0 and 1).

- `init_speed` The speed of the initial collision.

- `obj1_modes` The object's modes.

- `obj2_modes` The other object's modes.

***

## Functions

#### \_\_init\_\_

**`CollisionAudioInfo(obj1_modes, obj2_modes)`**

**`CollisionAudioInfo(amp=0.5, init_speed=1, obj1_modes, obj2_modes)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| amp |  float  | 0.5 | Amplitude of the first collision (must be between 0 and 1). |
| init_speed |  float  | 1 | The speed of the initial collision (all collisions will be scaled relative to this). |
| obj1_modes |  Modes |  | The object's modes. |
| obj2_modes |  Modes |  | The other object's modes. |

#### count_collisions

**`self.count_collisions()`**

Update the counter for how many times two objects have collided.

