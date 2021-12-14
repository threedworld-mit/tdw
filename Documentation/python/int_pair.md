# IntPair

`from tdw.int_pair import IntPair`

A pair of unordered hashable integers. Use this class for dictionary keys.

```python
import numpy as np
from tdw.int_pair import IntPair

id_0 = 0
pos_0 = np.array([0, 1, 0])
id_1 = 1
pos_1 = np.array([-2, 2.5, 0.8])
# Start a dictionary of distances between objects.
distances = {IntPair(id_0, id_1): np.linalg.norm(pos_0 - pos_1)}
```

***

## Fields

- `int1` The first integer.

- `int2` The second integer.

***

## Functions

#### \_\_init\_\_

**`IntPair(int1, int2)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| int1 |  int |  | The first integer. |
| int2 |  int |  | The second integer. |

