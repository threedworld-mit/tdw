# ClothMaterial

`from tdw.obi_data.cloth.cloth_material import ClothMaterial`

An Obi cloth material. For more information, [read this](http://obi.virtualmethodstudio.com/tutorials/clothsetup.html).

***

## Fields

- `visual_material` The name of the visual material associated with this cloth material.

- `texture_scale` The texture scale of the visual material.

- `visual_smoothness` The smoothness value of the visual material.

- `stretching_scale` The scale factor for the rest length of each constraint.

- `stretch_compliance` Controls how much constraints will resist a change in length.

- `max_compression` The percentage of compression allowed by the constraints before kicking in.

- `max_bending` The amount of bending allowed before the constraints kick in, expressed in world units.

- `bend_compliance` Controls how much constraints will resist a change in curvature, once they are past the maximum bending threshold.

- `drag` How much drag affects the cloth. The value is multiplied by the air density value.

- `lift` How much lift affects the cloth. The value is multiplied by the air density value.

- `mass_per_square_meter` The mass in kg per square meter of cloth surface area.

***

## Functions

#### \_\_init\_\_

**`ClothMaterial(visual_material, texture_scale)`**

**`ClothMaterial(visual_material, texture_scale, visual_smoothness=0, stretching_scale=1.0, stretch_compliance=0, max_compression=0, max_bending=0.05, bend_compliance=0, drag=0.05, lift=0.05, mass_per_square_meter=1)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| visual_material |  str |  | The name of the visual material associated with this cloth material. |
| texture_scale |  Dict[str, float] |  | The texture scale of the visual material. |
| visual_smoothness |  float  | 0 | The smoothness value of the visual material. |
| stretching_scale |  float  | 1.0 | The scale factor for the rest length of each constraint. |
| stretch_compliance |  float  | 0 | Controls how much constraints will resist a change in length. |
| max_compression |  float  | 0 | The percentage of compression allowed by the constraints before kicking in. |
| max_bending |  float  | 0.05 | The amount of bending allowed before the constraints kick in, expressed in world units. |
| bend_compliance |  float  | 0 | Controls how much constraints will resist a change in curvature, once they are past the maximum bending threshold. |
| drag |  float  | 0.05 | How much drag affects the cloth. The value is multiplied by the air density value. |
| lift |  float  | 0.05 | How much lift affects the cloth. The value is multiplied by the air density value. |
| mass_per_square_meter |  float  | 1 | The mass in kg per square meter of cloth surface area. |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.

