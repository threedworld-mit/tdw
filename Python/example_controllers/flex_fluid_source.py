from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from time import sleep

"""
Create a Flex FluidSource, or "hose pipe", simulation of a fluid stream.
"""

class FlexFluid(Controller):
    def run(self):
        self.load_streamed_scene(scene="tdw_room_2018")

        # Create the container, set up for fluids, and a "hose pipe" stream in particular.
        self.communicate({"$type": "create_flex_container",
                          "collision_distance": 0.05,
                          "static_friction": 0.1,
                          "dynamic_friction": 0.1,
                          "particle_friction": 0.1,
                          "solid_rest": 0.1,
                          "fluid_rest": 0.095,
                          "viscocity": 0,
                          "cohesion": 0.02,
                          "surface_tension": 0.01,
                          "radius": 0.25,
                          "damping": 0,
                          "substep_count": 2,
                          "iteration_count": 5,
                          "buoyancy": 1.0,
                          "anisotropy_scale": 1.5,
                          "max_particles": 15000,
                          "max_neighbors": 200})

        self.communicate({"$type": "set_time_step", "time_step": 0.02})

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 3.6, "y": 1.8, "z": 1.3}, look_at={"x": 0, "y": 1.35, "z": -2}))

        # Add the fluid source object, rotated so the fluid hits the wall.
        self.fluid_id = self.get_unique_id()
        self.communicate([{"$type": "load_flex_fluid_source_from_resources",
                           "id": self.fluid_id, "orientation": {"x": 44, "y": 0, "z": 0},
                           "position": {"x": 0, "y": 1.0, "z": 0}},
                          {"$type": "scale_object",
                           "id": self.fluid_id,
                           "scale_factor": {"x": 0.4, "y": 0.4, "z": 1}}])

        # Create the fluid source actor, assign its container and set the Flex object scale to a reasonable size for a water jet.
        self.communicate([{"$type": "create_flex_fluid_source_actor",
                           "id": self.fluid_id,
                           "mass_scale": 1.0,
                           "start_speed": 5.0,
                           "lifetime": 3.0,
                           "mesh_tesselation": 2},
                          {"$type": "assign_flex_container",
                           "id": self.fluid_id,
                           "container_id": 0, "fluid_container": True},
                          ])

        # Start an infinite loop to allow the build to simulate physics.
        while True:
            self.communicate({"$type": "step_physics", "frames":1})

if __name__ == "__main__":
    FlexFluid().run()
