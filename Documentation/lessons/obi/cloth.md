##### Physics (Obi)

# Cloth

In TDW's implementation of Obi, there are two types of cloth:

1. **Sheets** are two-dimensional squares that can optionally be **tethered** in-place.
2. **Volumes** are three-dimensional objects that can be **pressurized**. They are much more similar to standard TDW objects but have a more limited number of shapes.

## Sheets

To add an Obi cloth sheet to the scene, call `obi.create_cloth_sheet()`, which sends two commands: [`add_material`](../../api/command_api.md#add_material) (downloads and loads into memory the cloth sheet's [visual material](.../objects_and_scenes/materials_textures_colors.md)) and [`create_obi_cloth_sheet`](../../api/command_api.md#create_obi_cloth_sheet).

This is a minimal example of how to create a cloth sheet:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_cloth_sheet(cloth_material="cotton",
                       object_id=Controller.get_unique_id(),
                       position={"x": 0, "y": 2, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0})
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="iron_box",
                                                  object_id=Controller.get_unique_id()))
c.communicate(commands)
# Let the cloth fall.
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

**TODO**

### Sheet types

There are three [`SheetType`](../../python/obi_data/cloth/sheet_type.md) values, which can be set via the optional `sheet_type` parameter:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.sheet_type import SheetType

c = Controller()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_cloth_sheet(cloth_material="cotton",
                       object_id=Controller.get_unique_id(),
                       position={"x": 0, "y": 2, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       sheet_type=SheetType.cloth_vhd)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="iron_box",
                                                  object_id=Controller.get_unique_id()))
c.communicate(commands)
# Let the cloth fall.
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

**TODO**

Each `SheetType` has a different density of particles. Sheets with less particles will be more performant but will yield a coarser simulation. `SheetType.cloth` looks more like crumpled paper, in comparison to `SheetType.cloth_vhd`.

### Tethering

A portion of a cloth sheet can be **tethered** in-place. Cloth sheets by default aren't tethered. Cloth sheets may have more than one tether.

To add tethered positions,  set the `tether_positions` parameter in `obi.create_cloth_sheet()`. This is a dictionary where the key is a [`TetherParticleGroup`](../../python/obi_data/cloth/tether_particle_group.md) and the value is an object ID. If it's the ID of another object, the cloth will be tethered to that object. If it's the same ID as the sheet's ID, then the cloth will be suspended in mid-air.

This example tethers a cloth sheet at multiple positions in mid-air:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.sheet_type import SheetType
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup

c = Controller()
cloth_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
obi.create_cloth_sheet(cloth_material="plastic",
                       object_id=cloth_id,
                       position={"x": 1, "y": 1.0, "z": -1},
                       rotation={"x": 20, "y": 10, "z": 10},
                       sheet_type=SheetType.cloth_hd,
                       tether_positions={TetherParticleGroup.north_edge: cloth_id,
                                         TetherParticleGroup.east_edge: cloth_id})
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

**TODO**

**TODO other tether parameters**

## Cloth volumes

To add a cloth volume to the scene, call `obi.create_cloth_volume()`, which sends two commands: [`add_material`](../../api/command_api.md#add_material) (downloads and loads into memory the cloth volume's [visual material](.../objects_and_scenes/materials_textures_colors.md)) and [`create_obi_cloth_volume`](../../api/command_api.md#create_obi_cloth_volume).

This is a minimal example of how to create a cloth volume:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.volume_type import ClothVolumeType

c = Controller()
cloth_id = Controller.get_unique_id()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 0.5, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
# Add the cloth volume.
obi.create_cloth_volume(cloth_material="canvas",
                        object_id=cloth_id,
                        position={"x": 0, "y": 1.0, "z": 0},
                        rotation={"x": 0, "y": 0, "z": 0},
                        volume_type=ClothVolumeType.sphere,
                        pressure=3.0,
                        solver_id=0)
c.communicate(TDWUtils.create_empty_room(12, 12))
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

**TODO**

- The `volume_type` parameter accepts a [`VolumeType`](../..python/obi_data/cloth/volume_type.md) value.
- The `pressure` parameter determines how pressurized the volume is; in this example, the sphere behaves like a somewhat deflated ball.

## Cloth materials

Both `obi.create_cloth_sheet()` and `obi.create_cloth_volume()` have a `cloth_material` parameter. A cloth material is Obi physics parameters for the cloth plus its visual appearance.

 `cloth_material` can be set to either a preset cloth material (in which case the value is a string) or a custom cloth material (in which case the value is a [`ClothMaterial`](../../python/obi_data/cloth/cloth_material.md)). 

To get a dictionary of cloth material presets, do this:

```python
from tdw.obi_data.cloth.cloth_material import CLOTH_MATERIALS

for cloth_name in CLOTH_MATERIALS:
    print(cloth_name)
```

Output:

```
silk
cotton
wool
canvas
burlap
rubber
plastic
```

This example controller uses a custom cloth material:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.cloth_material import ClothMaterial

c = Controller()
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
cloth_material = ClothMaterial(visual_material="cotton_natural_rough",
                               texture_scale={"x": 2, "y": 2},
                               stretching_scale=1,
                               stretch_compliance=0,
                               max_compression=0,
                               max_bending=0.05,
                               drag=0,
                               lift=0,
                               tether_compliance=0,
                               tether_scale=1)
obi.create_cloth_sheet(cloth_material=cloth_material,
                       object_id=Controller.get_unique_id(),
                       position={"x": 0, "y": 2, "z": 0},
                       rotation={"x": 0, "y": 0, "z": 0})
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(Controller.get_add_physics_object(model_name="iron_box",
                                                  object_id=Controller.get_unique_id()))
c.communicate(commands)
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
```

Result:

**TODO**

This example creates a custom cloth material by copying most of the values from `CLOTH_MATERIALS["silk"]`:

```python
from tdw.obi_data.cloth.cloth_material import ClothMaterial, CLOTH_MATERIALS

# Get the preset silk material.
preset_material = CLOTH_MATERIALS["silk"]
# Use all of the parameters of the preset.
custom_material = ClothMaterial(**preset_material.__dict__)
# Set a custom visual material and texture scale.
custom_material.visual_material = "silk_smooth_red"
custom_material.texture_scale = {"x": 1, "y": 1}
```

## Solver parameters

Call `obi.set_solver()` to set the number of substeps and the scale of the solver. Scaling the solver will scale all Obi actors uniformly. This is the best way to scale a cloth actor.

This example tethers a cloth sheet to a bar-shaped object, which is then rotated. Note that we set the scale of the solver to resize the cloth:

```python
from tdw.controller import Controller
from tdw.add_ons.obi import Obi
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.obi_data.cloth.tether_particle_group import TetherParticleGroup
from tdw.obi_data.cloth.sheet_type import SheetType

c = Controller()
c.communicate(Controller.get_add_scene(scene_name="tdw_room"))
camera = ThirdPersonCamera(position={"x": -3.75, "y": 1.5, "z": -0.5},
                           look_at={"x": 0, "y": 1.25, "z": 0})
obi = Obi()
c.add_ons.extend([camera, obi])
cloth_id = Controller.get_unique_id()
cube_id = Controller.get_unique_id()
obi.set_solver(solver_id=0,
               substeps=2,
               scale_factor=0.5)
# Create a sheet that looks and behaves like canvas, that we will attach to a bar-shaped object.
# Note the offset in Z, required to line up the "north" edge of the sheet with the object.
obi.create_cloth_sheet(cloth_material="cotton",
                       object_id=cloth_id,
                       position={"x": 0, "y": 2.0, "z": -3.0},
                       rotation={"x": 0, "y": 0, "z": 0},
                       sheet_type=SheetType.cloth_vhd,
                       tether_positions={TetherParticleGroup.north_edge: cube_id})
# Create the long bar-shaped attachment object.
c.communicate(Controller.get_add_physics_object(model_name="cube",
                                                object_id=cube_id,
                                                library="models_flex.json",
                                                position={"x": 0, "y": 2.0, "z": 0},
                                                kinematic=True,
                                                gravity=False,
                                                scale_factor={"x": 3.0, "y": 0.1, "z": 0.1}))
# Let the cloth object settle.
for i in range(150):
    c.communicate([])
# Rotate the bar back and forth, moving the cloth with it.
for i in range(480):
    c.communicate({"$type": "rotate_object_by",
                   "id": cube_id,
                   "axis": "yaw",
                   "is_world": False,
                   "angle": 1})
for i in range(540):
    c.communicate({"$type": "rotate_object_by",
                   "id": cube_id,
                   "axis": "yaw",
                   "is_world": False,
                   "angle": -1})
c.communicate({"$type": "terminate"})
```

Result:

**TODO**