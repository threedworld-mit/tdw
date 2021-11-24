##### 3D Model Libraries

# Free models

"Free" models are models that don't require special access privlieges to use in TDW. They exist on an S3 server and have public URLs.

The "core" model library is the largest free model library in TDW and the most commonly used. There are two other free model libraries:

## `models_special.json`

`models_special.json` includes special-case models for particular use-cases. It also includes some primitives:

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian("models_special.json")
for record in librarian.records:
    print(record.name)
```

Output:

```
cloth_1meter_square
cloth_square
fluid_receptacle1m_round
fluid_receptacle1x1
fluid_receptacle1x2
new_ramp
prim_capsule
prim_cone
prim_cube
prim_cyl
prim_sphere
ramp_scene_max
ramp_with_platform
```

It's possible that you'll want to use the `prim_` models if you need to add primitive shapes to a simulation. The `cloth_` and `fluid_` models are used in certain [Flex simulations](../flex/flex.md). 

## `models_flex.json`

`models_flex.json` contains primitives that have been optimized for [Flex simulations](../flex/flex.md).

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian("models_flex.json")
for record in librarian.records:
    print(record.name)
```

Output:

```
bowl
cone
cube
cylinder
dumbbell
octahedron
pentagon
pipe
platonic
pyramid
sphere
torus
triangular_prism
```

***

**Next: [Non-free models](non_free_models.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`ModelLibrarian`](../../python/librarian/model_librarian.md)

