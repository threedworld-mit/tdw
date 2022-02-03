# LateralSubArrangement

`from tdw.add_ons.proc_gen_objects_data.lateral_sub_arrangement import LateralSubArrangement`

Data for a sub-arrangement of a lateral arrangement, for example a kitchen counter.
This contains the function that will be used to create the sub-arrangement.

***

## Functions

#### \_\_init\_\_

**`LateralSubArrangement(category, function)`**

**`LateralSubArrangement(category, function, position_offset_multiplier=1)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| category |  str |  | The proc-gen category. |
| function |  Callable[[ModelRecord, Dict[str, float] |  | The function that will be used to create the sub-arrangement. |
| position_offset_multiplier |  int  | 1 | After creating the sub-arrangement, offset the lateral arrangement position by the half of extents of the root object multiplied by this factor. |

