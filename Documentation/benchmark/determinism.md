# Physics Determinism

To benchmark how deterministic physics are in PhysX (not Flex), run the scripts in `benchmarking/variance`

These tests require [`tdw_physics`](https://github.com/alters-mit/tdw_physics).

### variance.py

This will test physics determinism between multiple trials. A lower value means that physics is more deterministic.

#### Result

0.5429648119664215

#### Optional arguments:

| Argument       | Default value        | Description                                                  |
| -------------- | -------------------- | ------------------------------------------------------------ |
| `--coll_mode`  | `continuous_dynamic` | The collision detection mode. Options: `continuous_dynamic`, `continuous`, `continuous_speculative`, `discrete` |
| `--num_trials` | 10                   | The number of trials for the test.                           |

***

### variance_avatar.py

This test will test physics determinism in a complex scene with a fast-moving Sticky Mitten Avatar.

The controller creates stacks of boxes and then an avatar moves through the boxes. The avatar's movements are random but pre-calculated. See: `VarianceAvatar.precalculate_commands()` This means that the movements are the same for every trial and test. The avatar movements are very sudden. This is intentional, as it should put stress on the physics engine.

#### Result

| Detection Mode         | Variance          |
| ---------------------- | ----------------- |
| continuous             | 6.150372665026829 |
| continuous_speculative | 8.24157560373599  |
| continuous_dynamic     | 6.309563034365061 |
| discrete               | 6.898498771395887 |

#### Optional arguments:

| Argument         | Default value | Description                             |
| ---------------- | ------------- | --------------------------------------- |
| `--num_trials`   | 10            | The number of trials for the test.      |
| `--precalculate` |               | Precalculate movements.                 |
| `--num_frames`   | 300           | Number of frames until a trial is done. |