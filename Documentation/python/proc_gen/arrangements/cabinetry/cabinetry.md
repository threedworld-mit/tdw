# Cabinetry

`from tdw.proc_gen.arrangements.cabinetry.cabinetry import Cabinetry`

A set of cabinetry models and materials.

***

## Fields

- `name` The name of the cabinetry set.

- `kitchen_counters` A list of names of kitchen counter models.

- `wall_cabinets` A list of names of wall cabinet models.

- `sinks` A list of names of kitchen sink models.

- `counter_top_material` The name of the kitchen countertop material.

***

## Functions

#### \_\_init\_\_

**`Cabinetry(name, kitchen_counters, wall_cabinets, sinks, counter_top_material)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  Union[str, CabinetryType] |  | The name of the cabinetry set. |
| kitchen_counters |  List[str] |  | A list of names of kitchen counter models. |
| wall_cabinets |  List[str] |  | A list of names of wall cabinet models. |
| sinks |  List[str] |  | A list of names of kitchen sink models. |
| counter_top_material |  str |  | The name of the kitchen countertop material. |
