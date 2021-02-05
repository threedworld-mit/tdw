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