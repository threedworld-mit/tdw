# ScrapeModel

`from tdw.physics_audio.scrape_model import ScrapeModel`

Data for a 3D model being used as a Clatter scrape surface.

***

## Fields

- `model_name` The name of the model.

- `sub_objects` A list of [sub-objects that will be used as scrape surfaces](scrape_sub_object.md).

- `scrape_material` The [scrape material](scrape_material.md).

- `visual_material` The name of the new visual material.

***

## Functions

#### \_\_init\_\_

**`ScrapeModel(model_name, sub_objects, visual_material, scrape_material)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_name |  str |  | The name of the model. |
| sub_objects |  List[ScrapeSubObject] |  | A list of [sub-objects that will be used as scrape surfaces](scrape_sub_object.md). |
| visual_material |  str |  | The name of the new visual material. |
| scrape_material |  ScrapeMaterial |  | The [scrape material](scrape_material.md). |

