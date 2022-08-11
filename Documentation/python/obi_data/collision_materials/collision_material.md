# CollisionMaterial

`from tdw.obi_data.collision_materials.collision_material import CollisionMaterial`

Data for an Obi collision material.

***

## Fields

- `dynamic_friction` Percentage of relative tangential velocity removed in a collision, once the static friction threshold has been surpassed and the particle is moving relative to the surface. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.

- `static_friction` Percentage of relative tangential velocity removed in a collision. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.

- `stickiness` Amount of inward normal force applied between objects in a collision. 0 means no force will be applied, 1 will keep objects from separating once they collide.

- `stick_distance` Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated.

- `friction_combine` A [`MaterialCombineMode`](material_combine_mode.md). How is the friction coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different friction combine modes, the mode with the lowest enum index is used.

- `stickiness_combine` A [`MaterialCombineMode`](material_combine_mode.md). How is the stickiness coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different stickiness combine modes, the mode with the lowest enum index is used.

***

## Functions

#### \_\_init\_\_

**`CollisionMaterial()`**

**`CollisionMaterial(dynamic_friction=0.3, static_friction=0.3, stickiness=0, stick_distance=0, friction_combine=MaterialCombineMode.average, stickiness_combine=MaterialCombineMode.average)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| dynamic_friction |  float  | 0.3 | Percentage of relative tangential velocity removed in a collision, once the static friction threshold has been surpassed and the particle is moving relative to the surface. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity. |
| static_friction |  float  | 0.3 | Percentage of relative tangential velocity removed in a collision. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity. |
| stickiness |  float  | 0 | Amount of inward normal force applied between objects in a collision. 0 means no force will be applied, 1 will keep objects from separating once they collide. |
| stick_distance |  float  | 0 | Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated. |
| friction_combine |  MaterialCombineMode  | MaterialCombineMode.average | A [`MaterialCombineMode`](material_combine_mode.md). How is the friction coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different friction combine modes, the mode with the lowest enum index is used. |
| stickiness_combine |  MaterialCombineMode  | MaterialCombineMode.average | A [`MaterialCombineMode`](material_combine_mode.md). How is the stickiness coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different stickiness combine modes, the mode with the lowest enum index is used. |

#### to_dict

**`self.to_dict()`**

_Returns:_  A JSON dictionary of this object.

