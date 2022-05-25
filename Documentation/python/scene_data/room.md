# Room

`from scene_data.room import Room`

A room in an interior environment. Rooms can be comprised of multiple box-shaped [regions](interior_region.md).
Each room has 1 main region and *n* alcove regions.
For example, an L shaped room has a main region ( `|` ) and one alcove ( `_` ).

***

## Fields

- `main_region` The main [`InteriorRegion`](interior_region.md).

- `alcoves` A list of alcove regions. Can be an empty list.

***

## Functions

#### \_\_init\_\_

**`Room(main_region, alcoves)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| main_region |  InteriorRegion |  | The main [`InteriorRegion`](interior_region.md). |
| alcoves |  List[InteriorRegion] |  | A list of alcove regions. Can be an empty list. |

