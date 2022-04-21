# TetherType

`from tdw.obi_data.cloth.tether_type import TetherType`

A type of an Obi cloth tether position.

***

## Fields

- `object_id` The object ID. If this is the same as the cloth's ID, the cloth will be suspended in mid-air.

- `is_static` If True, this is a static tether attachment. If False, this is a dynamic tether attachment.

***

## Functions

#### \_\_init\_\_

**`TetherType(object_id)`**

**`TetherType(object_id, is_static=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The object ID. If this is the same as the cloth's ID, the cloth will be suspended in mid-air. |
| is_static |  bool  | True | If True, this is a static tether attachment. If False, this is a dynamic tether attachment. |

