# TableAndChairs

`from proc_gen.arrangements.table_and_chairs import TableAndChairs`

Abstract base class for a table with chairs around it.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. |

***

## Functions

#### \_\_init\_\_

**`TableAndChairs(used_walls, region, model, position, rng)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| used_walls |  int |  | Bitwise sum of walls with objects. |
| region |  InteriorRegion |  | The [`InteriorRegion`](../../scene_data/interior_region.md) that the table is in. |
| model |  Union[str, ModelRecord] |  | Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| rng |  np.random.RandomState |  | The random number generator. |

#### get_commands

**`self.get_commands()`**

_Returns:_  The category of the chair models.

