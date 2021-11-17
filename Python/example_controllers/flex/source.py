from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.flex_data.fluid_type import FLUID_TYPES

"""
Create a Flex FluidSource, or "hose pipe", simulation of a fluid stream.
"""

c = Controller()
fluid = FLUID_TYPES["water"]
fluid_id = c.get_unique_id()
# Load the scene. Create a Flex container.
# Load the fluid source object and scale it.
# Create the fluid source actor, assign its container and set the scale to a reasonable size for a water jet.
commands = [c.get_add_scene(scene_name="tdw_room"),
            {"$type": "create_flex_container",
             "collision_distance": 0.05,
             "static_friction": 0.1,
             "dynamic_friction": 0.1,
             "particle_friction": 0.1,
             "solid_rest": 0.1,
             "fluid_rest": 0.095,
             "viscocity": fluid.viscosity,
             "cohesion": fluid.cohesion,
             "adhesion": fluid.adhesion,
             "surface_tension": 0.01,
             "radius": 0.25,
             "damping": 0,
             "substep_count": 2,
             "iteration_count": 5,
             "buoyancy": 1.0,
             "anisotropy_scale": 1.5,
             "max_particles": 15000,
             "max_neighbors": 200},
            {"$type": "load_flex_fluid_source_from_resources",
             "id": fluid_id,
             "orientation": {"x": 44, "y": 0, "z": 0},
             "position": {"x": 0, "y": 1.0, "z": 0}},
            {"$type": "scale_object",
             "id": fluid_id,
             "scale_factor": {"x": 0.4, "y": 0.4, "z": 1}},
            {"$type": "set_flex_fluid_source_actor",
             "id": fluid_id,
             "mass_scale": 1.0,
             "start_speed": 5.0,
             "lifetime": 3.0,
             "mesh_tesselation": 2},
            {"$type": "assign_flex_container",
             "id": fluid_id,
             "container_id": 0,
             "fluid_container": True},
            {"$type": "set_time_step",
             "time_step": 0.02}]
# Add an avatar.
commands.extend(TDWUtils.create_avatar(position={"x": 3.6, "y": 1.8, "z": 1.3}, look_at={"x": 0, "y": 1.35, "z": -2}))
c.communicate(commands)

for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
