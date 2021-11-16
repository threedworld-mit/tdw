##### Physics (Flex)

# Fluid and source actors

In Flex simulations *fluids* are bodies of fluids while *sources* are fluids emitted from a source.

## Fluid simulations and Flex containers

Like all Flex simulations, fluid simulations require a Flex container. The parameters `"viscosity"`, `"adhesion"`, and `"cohesion"` control the fluid dynamics.

TDW includes pre-set values for various types of fluids. You can find these in the [`FluidTypes`](../../python/fluid_types.md) class:

```python
from tdw.flex.fluid_types import FluidTypes

ft = FluidTypes()
print(ft.fluid_type_names)
water = ft.fluid_types["water"]
print(water.fluid_type)
print(water.adhesion)
print(water.viscosity)
print(water.cohesion)
```

Output:

```
['water', 'ink', 'oil', 'honey', 'glycerin', 'chocolate']
water
0
0.01
0.001
```

You can then use these parameters in [`create_flex_container`](../../api/command_api.md#create_flex_container):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.flex.fluid_types import FluidTypes

fluid = FluidTypes().fluid_types["honey"]
c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {'$type': 'convexify_proc_gen_room'},
               {"$type": "create_flex_container",
                "collision_distance": 0.04,
                "static_friction": 0.1,
                "dynamic_friction": 0.1,
                "particle_friction": 0.1,
                "viscocity": fluid.viscosity,
                "adhesion": fluid.adhesion,
                "cohesion": fluid.cohesion,
                "radius": 0.1,
                "fluid_rest": 0.05,
                "damping": 0.01,
                "substep_count": 5,
                "iteration_count": 8,
                "buoyancy": 1.0}])
```

In this example, fluids are parameterized and randomly selected:

```python
import random
from tdw.controller import Controller
from tdw.flex.fluid_types import FluidTypes


class FlexFluids(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.fluid_types = FluidTypes()
        self.communicate(self.get_add_scene(scene_name="tdw_room"))
        
    def trial(self, fluid_name: str) -> None:
        fluid = self.fluid_types.fluid_types[fluid_name]
        self.communicate([{"$type": "create_flex_container",
                           "collision_distance": 0.04,
                           "static_friction": 0.1,
                           "dynamic_friction": 0.1,
                           "particle_friction": 0.1,
                           "viscocity": fluid.viscosity,
                           "adhesion": fluid.adhesion,
                           "cohesion": fluid.cohesion,
                           "radius": 0.1,
                           "fluid_rest": 0.05,
                           "damping": 0.01,
                           "substep_count": 5,
                           "iteration_count": 8,
                           "buoyancy": 1.0}])
        
    def run(self, num_trials: int) -> None:
        for i in range(num_trials):
            # Select a random fluid.
            fluid_name = random.choice(self.fluid_types.fluid_type_names)
            self.trial(fluid_name=fluid_name)
        self.communicate({"$type": "terminate"})

if __name__ == "__main__":
    c = FlexFluids()
    c.run(num_trials=15)
```

## Fluid actors

A fluid actor requires at least two objects: An object to hold the fluid (a *receptacle*) and the fluid object.

The best object to use as a receptacle is `fluid_receptacle1x1`, found in `models_special.json`. It does *not* need to be a Flex-enabled object.

The fluid body is a data file located with the TDW build (as opposed to an asset bundle). Load it via [`load_flex_fluid_from_resources`](../../api/command_api.md#load_flex_fluid_from_resources). Make the fluid body a fluid actor via [`create_flex_fluid_object`](../../api/command_api.md#create_flex_fluid_object).

When using fluids, set the parameter `"fluid_container"` to True and set `"fluid_type"` to the name of the fluid in [`assign_flex_container`](../../api/command_api.md#assign_flex_container).

This example adds a random fluid to each trial:

```python
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.flex.fluid_types import FluidTypes


class FlexFluids(Controller):
    """
    Generate fluid simulation trials with random fluids.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.fluid_types = FluidTypes()
        # Create a scene and add a camera.
        commands = [self.get_add_scene(scene_name="tdw_room")]
        commands.extend(TDWUtils.create_avatar(position={"x": -3.75, "y": 1.5, "z": -0.5},
                                               look_at={"x": 0, "y": 0, "z": 0},
                                               avatar_id="a"))
        self.communicate(commands)

    def trial(self, fluid_name: str) -> None:
        fluid = self.fluid_types.fluid_types[fluid_name]
        receptacle_id = self.get_unique_id()
        fluid_id = self.get_unique_id()
        # Create a Flex fluid container.
        # Add a receptacle and a fluid object.
        self.communicate([{"$type": "create_flex_container",
                           "collision_distance": 0.04,
                           "static_friction": 0.1,
                           "dynamic_friction": 0.1,
                           "particle_friction": 0.1,
                           "viscocity": fluid.viscosity,
                           "adhesion": fluid.adhesion,
                           "cohesion": fluid.cohesion,
                           "radius": 0.1,
                           "fluid_rest": 0.05,
                           "damping": 0.01,
                           "substep_count": 5,
                           "iteration_count": 8,
                           "buoyancy": 1.0},
                          self.get_add_object(model_name="fluid_receptacle1x1",
                                              object_id=receptacle_id,
                                              position={"x": -0.35, "y": 0, "z": 0},
                                              rotation={"x": 0, "y": 0, "z": 0},
                                              library="models_special.json"),
                          {"$type": "scale_object",
                           "id": receptacle_id,
                           "scale_factor": {"x": 2.0, "y": 2.0, "z": 2.0}},
                          {"$type": "set_kinematic_state",
                           "id": receptacle_id,
                           "is_kinematic": True,
                           "use_gravity": False},
                          {"$type": "load_flex_fluid_from_resources",
                           "id": fluid_id,
                           "orientation": {"x": 0, "y": 0, "z": 0},
                           "position": {"x": -0.35, "y": 1.0, "z": 0}},
                          {"$type": "create_flex_fluid_object",
                           "id": fluid_id,
                           "mass_scale": 1.0,
                           "particle_spacing": 0.05},
                          {"$type": "assign_flex_container",
                           "id": fluid_id,
                           "container_id": 0,
                           "fluid_container": True,
                           "fluid_type": fluid_name}])
        # Let the fluid move.
        for i in range(200):
            self.communicate([])
        # Reset the scene.
        self.communicate([{"$type": "destroy_flex_container"},
                          {"$type": "destroy_object",
                           "id": receptacle_id},
                          {"$type": "destroy_flex_object",
                           "id": fluid_id}])

    def run(self, num_trials: int) -> None:
        for i in range(num_trials):
            # Select a random fluid.
            fluid_name = random.choice(self.fluid_types.fluid_type_names)
            self.trial(fluid_name=fluid_name)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = FlexFluids()
    c.run(num_trials=15)
```

Note: Each trial ends with three commands: [`destroy_flex_container`](../../api/command_api.md#destroy_flex_container), [`destroy_object`](../../api/command_api.md#destroy_object), and [`destroy_flex_object`](../../api/command_api.md#destroy_flex_object). [A document later in this tutorial will explain in more depth how to reset a Flex scene.](reset_scene.md) The command `destroy_object` is used for the receptacle because it isn't a Flex object.

## Limitations

- Flex fluid and source actors are only supported on Windows.
- [Flex particle output data](output_data.md) is disabled if there are fluid or source actors in the scene.

