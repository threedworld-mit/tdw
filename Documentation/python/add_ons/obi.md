# Obi

`from tdw.add_ons.obi import Obi`

This add-on handles most aspects of an Obi physics simulation, including initialization, actor creation, and particle output data.

***

## Fields

- `actors` A dictionary of Obi actor data. Key = Object ID. Value = [`ObiActor`](../obi_data/obi_actor.md). The particle data is updated if `output_data == True` (see above).

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`Obi()`**

**`Obi(output_data=True, floor_material=None, object_materials=None, vr_material=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| output_data |  bool  | True | If True, receive [`ObiParticles`](../../api/output_data.md#ObiParticles) per frame. |
| floor_material |  CollisionMaterial  | None | The floor's [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values. |
| object_materials |  Dict[int, CollisionMaterial] | None | Overrides for object and robot collision materials. Key = Object or Robot ID. Value = [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). |
| vr_material |  CollisionMaterial  | None | If there is a VR rig in the scene, its hands will have this [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### create_fluid

**`self.create_fluid(object_id, fluid, shape)`**

**`self.create_fluid(object_id, fluid, shape, position=None, rotation=None, speed=0, lifespan=4, minimum_pool_size=0.5, solver_id=0)`**

Create a cube-shaped fluid emitter.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The unique ID of the emitter. |
| fluid |  Union[str, Fluid, GranularFluid] |  | Either a [`Fluid`](../obi_data/fluids/fluid.md), a [`GranularFluid`](../obi_data/fluids/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`). |
| shape |  EmitterShape |  | Either a [`CubeEmitter`](../obi_data/fluids/cube_emitter.md), [`DiskEmitter`](../obi_data/fluids/disk_emitter.md), [`EdgeEmitter`](../obi_data/fluids/edge_emitter.md), or [`SphereEmitter`](../obi_data/fluids/sphere_emitter.md). |
| position |  Dict[str, float] | None | The position of the emitter object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The rotation of the emitter object, in Euler angles.  If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| speed |  float  | 0 | The speed of emission in meters per second. If 0, there is no emission. |
| lifespan |  float  | 4 | The particle lifespan in seconds. |
| minimum_pool_size |  float  | 0.5 | The minimum amount of inactive particles available before the emitter is allowed to resume emission. |
| solver_id |  int  | 0 | The ID of the Obi solver. |

#### create_cloth_sheet

**`self.create_cloth_sheet(object_id, cloth_material)`**

**`self.create_cloth_sheet(object_id, cloth_material, sheet_type=SheetType.cloth_hd, position=None, rotation=None, solver_id=0, tether_positions=None)`**

Create a cloth sheet.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The unique ID of the cloth sheet. |
| cloth_material |  Union[str, ClothMaterial] |  | Either a [`ClothMaterial`](../obi_data/cloth/cloth_material.md) or the name of a cloth material (see `Cloth.CLOTH_MATERIALS`)). |
| sheet_type |  SheetType  | SheetType.cloth_hd | The [`SheetType`](../obi_data/cloth/sheet_type.md). |
| position |  Dict[str, float] | None | The position of the cloth sheet. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The rotation of the cloth sheet, in Euler angles.  If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| solver_id |  int  | 0 | The ID of the Obi solver. |
| tether_positions |  Dict[TetherParticleGroup, TetherType] | None | An dictionary of tether positions. Key = [`TetherParticleGroup`](../obi_data/cloth/tether_particle_group.md). Value = [`TetherType`](../obi_data/cloth/tether_type.md). Can be None. |

#### create_cloth_volume

**`self.create_cloth_volume(object_id, cloth_material, volume_type)`**

**`self.create_cloth_volume(object_id, cloth_material, position=None, rotation=None, scale_factor=None, pressure=0.5, volume_type, solver_id=0)`**

Create a cloth volume.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The unique ID of the cloth sheet. |
| cloth_material |  Union[str, ClothMaterial] |  | Either a [`ClothMaterial`](../obi_data/cloth/cloth_material.md) or the name of a cloth material (see `Cloth.CLOTH_MATERIALS`)). |
| position |  Dict[str, float] | None | The position of the cloth volume. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The rotation of the cloth volume, in Euler angles.  If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| scale_factor |  Dict[str, float] | None | The scale factor of the mesh. If None, defaults to `{"x": 1, "y": 1, "z": 1}`. |
| pressure |  float  | 0.5 | The inflation amount of this cloth volume. |
| volume_type |  ClothVolumeType |  | The [`VolumeType`](../obi_data/cloth/volume_type.md). |
| solver_id |  int  | 0 | The ID of the Obi solver. |

#### set_fluid_speed

**`self.set_fluid_speed(object_id, speed)`**

Set the speed of a fluid emitter. By default, the speed of an emitter is 0 (no fluid emission).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the fluid emitter. |
| speed |  float |  | The speed in meters per second. Set this to 0 to stop emission. |

#### apply_force_to_cloth

**`self.apply_force_to_cloth(object_id)`**

**`self.apply_force_to_cloth(object_id, force=None, torque=None, force_mode=ForceMode.impulse)`**

Apply a uniform force and/or torque to a cloth actor.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the cloth actor. |
| force |  Dict[str, float] | None | The force. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| torque |  Dict[str, float] | None | The torque. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| force_mode |  ForceMode  | ForceMode.impulse | The [`ForceMode`](../obi_data/force_mode.md) for the `force` and/or `torque`. |

#### untether_cloth_sheet

**`self.untether_cloth_sheet(object_id, tether_position)`**

Untether a cloth sheet.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| object_id |  int |  | The ID of the cloth sheet. |
| tether_position |  TetherParticleGroup |  | The [`TetherParticleGroup`](../obi_data/cloth/tether_particle_group.md) describing the position. |

#### set_solver

**`self.set_solver()`**

**`self.set_solver(solver_id=0, substeps=1, scale_factor=1)`**

Set the parameters of a solver.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| solver_id |  int  | 0 | The solver ID. |
| substeps |  int  | 1 | The number of substeps. More substeps can increase accuracy at the cost of performance. |
| scale_factor |  float  | 1 | The scale of the solver. This will uniformly scale all objects assigned to the solver. |

#### reset

**`self.reset()`**

**`self.reset(floor_material=None, object_materials=None, vr_material=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| floor_material |  CollisionMaterial  | None | The floor's [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values. |
| object_materials |  Dict[int, CollisionMaterial] | None | Overrides for object and robot collision materials. Key = Object or Robot ID. Value = [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). |
| vr_material |  CollisionMaterial  | None | If there is a VR rig in the scene, its hands will have this [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values. |