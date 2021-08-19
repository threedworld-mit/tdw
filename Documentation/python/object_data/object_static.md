# ObjectStatic

`from object_data.object_static import ObjectStatic`

Static data for an object. This data won't change between frames.

***

## Fields

- `object_id` The unique ID of the object.

- `name` [The name of the model.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/model_librarian.md)

- `category` The semantic category of the object.

- `kinematic` If True, this object is kinematic, and won't respond to physics. 
Examples: a painting hung on a wall or built-in furniture like a countertop.

- `segmentation_color` The RGB segmentation color for the object as a numpy array: `[r, g, b]`

- `mass` The mass of the object.

- `size` The size of the object as a numpy array: `[width, height, length]`

***

## Functions

#### \_\_init\_\_

**`ObjectStatic(name, object_id, mass, segmentation_color, size)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the object. |
| object_id |  int |  | The unique ID of the object. |
| mass |  float |  | The mass of the object. |
| segmentation_color |  np.array |  | The segmentation color of the object. |
| size |  np.array |  | The size of the object. |

