# Plate

`from proc_gen.arrangements.plate import Plate`

A kitchen plate.

- The plate model is chosen randomly; see `TableSetting.MODEL_CATEGORIES["plate"]`.
- The plate might have food on it; see `food_probability` in the constructor.
  - The possible food categories are `TableSetting.FOOD_CATEGORIES`.
  - See `TableSetting.MODEL_CATEGORIES` for a list of models within those categories.
  - The position of the food is perturbed randomly.
  - The rotation of the food is random.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `ON_TOP_OF` | Dict[str, List[str]] | A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category. |
| `ENCLOSED_BY` | Dict[str, List[str]] | A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category. |
| `INSIDE_OF` | Dict[str, List[str]] | A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category. |
| `FOOD_CATEGORIES` | List[str] | The categories of possible food models. |

***

## Functions

#### \_\_init\_\_

**`Plate(food_probability, model, position, rng)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| food_probability |  float |  | The probability of placing food on the plate. |
| model |  Union[str, ModelRecord] |  | Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`. |
| position |  Dict[str, float] |  | The position of the root object. This might be adjusted. |
| rng |  np.random.RandomState |  | The random number generator. |

#### get_commands

**`self.get_commands()`**

_Returns:_  A list of commands that will generate the arrangement.

