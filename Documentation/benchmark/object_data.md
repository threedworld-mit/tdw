# Object Data

Collecting object data in TDW is _very_ fast. These benchmarks measure the performance of each standard type of object data.

For more information on what sort of data is returned by each data type, read the [Output Data API](../api/output_data.md).

#### Arguments

| Argument        | Description                                        |
| --------------- | -------------------------------------------------- |
| `--boxes`       | Add 100 cube primitives to the scene.              |
| `--transforms`  | Send `Transforms` data (position, rotation, etc.). |
| `--rigidbodies` | Send `Rigidbodies` data (velocity, mass, etc.).    |
| `--collisions`  | Send `Collisions` data.                            |
| `--bounds`      | Send `Bounds` data.                                |

#### Results

| Test                                                       | FPS  |
| ---------------------------------------------------------- | ---- |
| `--boxes --transforms`                                     | 599  |
| `--boxes --rigidbodies`                                    | 642  |
| `--boxes --collisions`                                     | 654  |
| `--boxes --bounds`                                         | 396  |
| `--boxes --transforms --rigidbodies --collisions --bounds` | 308  |

### How to run this test

```bash
cd <root>/Python/benchmarking
python3 object_data.py
```

```bash
<run build>
```

