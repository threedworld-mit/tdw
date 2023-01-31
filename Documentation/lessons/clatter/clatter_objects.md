##### Clatter

# Object audio data

When the `Clatter` add-on initializes, it will request output data from the build to determine which objects in the scene. On the *next* communicate() call, `Clatter` will "clatterize" each object in the scene.

Every "clatterized" object has a audio-physical values that will determine what sort of sound it makes when it collides with another clatterized object. In the frontend TDW API, this data is stored as a [`ClatterObject`](../../python/physics_audio/clatter_object.md) class.

## Default object data

In TDW, many models have predefined `ClatterObject` values, which are stored in `DEFAULT_OBJECTS`:

```python
from tdw.physics_audio.clatter_object import DEFAULT_OBJECTS

for model_name in DEFAULT_OBJECTS:
    print(model_name)
    clatter_object = DEFAULT_OBJECTS[model_name]
```

The `Clatter` add-on will automatically apply the default `ClatterObject` data to objects in the scene.

## Derived object data

If there are objects in the scene that *aren't* stored in `DEFAULT_OBJECTS`, the `Clatter` add-on will automatically try to derive reasonable values for them based on existing pre-defined data. For example, if there is a fork in the scene, `Clatter` might use mean values of all of the forks in `DEFAULT_OBJECTS` for this new fork model.

There are a few ways to control how `ClatterObject` data is derived using constructor parameters:

- `environment` is either a [`ClatterObject`](../../python/physics_audio/clatter_object.md) or an [`ImpactMaterial`](../../python/physics_audio/impact_material.md) that sets the Clatter object data for the environment (i.e. the floor).
- `robot_material` is the [`ImpactMaterial`](../../python/physics_audio/impact_material.md) used for all robot joints.
- `default_object` is a [`ClatterObject`](../../python/physics_audio/clatter_object.md) used in situations in which all other attempts to derive `ClatterObject` data fail.

## User-defined object data

## Audio materials

In Clatter, there are two types of audio materials: [`ImpactMaterial`](../../python/physics_audio/impact_material.md) and [`ScrapeMaterial`](../../python/physics_audio/scrape_material.md)



