from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from time import sleep
from platform import system


"""
Create a fluid "container" with the NVIDIA Flex physics engine. Run several trials, dropping ball objects of increasing mass into the fluid.
"""


class FlexFluid(Controller):
    def run(self):
        if system() != "Windows":
            raise Exception("Flex fluids are only supported in Windows (see Documentation/misc_frontend/flex.md)")
        self.load_streamed_scene(scene="tdw_room_2018")

        # Create the container, set up for fluids.
        self.communicate({"$type": "create_flex_container",
                          "collision_distance": 0.04,
                          "static_friction": 0.1,
                          "dynamic_friction": 0.1,
                          "particle_friction": 0.1,
                          "viscocity": 0.001,
                          "cohesion": 0.0015,
                          "radius": 0.1,
                          "fluid_rest": 0.05,
                          "damping": 0.01,
                          "substep_count": 5,
                          "iteration_count": 5,
                          "buoyancy": 1.0})

        # Slow down physics so the water can settle without splashing out of the container.
        self.communicate({"$type": "set_time_step", "time_step": 0.005})

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": -3.75, "y": 1.5, "z": -0.5}, look_at={"x": 0, "y": 0, "z": 0}))
        
        # Load a pool container for the fluid.
        self.pool_id = self.add_object("fluid_receptacle1x1", position={"x": -0.35, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
        self.communicate([{"$type": "scale_object", "id": self.pool_id, "scale_factor": {"x": 2.0, "y": 2.0, "z":2.0}}, {"$type": "set_kinematic_state", "id": self.pool_id, "is_kinematic": True, "use_gravity": False}])

        # Add the fluid actor, using the FluidPrimitive.
        self.fluid_id = self.get_unique_id()
        self.communicate({"$type": "load_flex_fluid_from_resources", "id": self.fluid_id, "orientation": {"x": 0, "y": 0, "z": 0}, "position": {"x": -0.35, "y": 1.0, "z": 0}})

        # Assign the actor's container and set the Flex scale (this MUST be done, even if the scale is 1,1,1).
        self.communicate([{"$type": "create_flex_fluid_object",
                           "id": self.fluid_id,
                           "mass_scale": 1.0,
                           "particle_spacing": 0.05},
                          {"$type": "assign_flex_container",
                           "id": self.fluid_id,
                           "container_id": 0, "fluid_container": True}
                          ])

        # Pause for a while to look at the container while it fills with water (this is not required, simply for demo purposes).
        for i in range(500):
            # Look at the object.
            self.communicate({"$type": "look_at",
                              "avatar_id": "a",
                              "object_id": self.pool_id,
                              "use_centroid": True})

        # Set physics back to a normal rate, for the trials.
        self.communicate({"$type": "set_time_step", "time_step": 0.03})
        
        # Set up the data for five "trials" and run them.
        masses = [1.25, 2.5, 4.0, 6.65, 8.5]
        heights = [3.0, 3.0, 3.0, 3.0, 3.0]
        stim_times = [170, 170, 170, 170, 170]
        pause_times = [0.1, 0.1, 0.1, 0.1, 0.1]
        for mass, height, stim_time, pause_time in zip(masses, heights, stim_times, pause_times):
            self.do_trial(mass, height, stim_time, pause_time)


    def do_trial(self, obj_mass: float, height: float, stim_time: int, pause_time: int):
        # Add the sphere object.
        sphere_id = self.add_object("prim_sphere", position={"x": 0, "y": height, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
        self.communicate([{"$type": "scale_object", "id": sphere_id, "scale_factor": {"x": 0.4, "y": 0.4, "z": 0.4}}, {"$type": "set_kinematic_state", "id": sphere_id}])

        # Set the object to kinematic.
        # Set the solid actor.
        # Assign the actor's container.
        self.communicate([
                          {"$type": "set_flex_solid_actor",
                           "id": sphere_id,
                           "mass_scale": obj_mass,
                           "particle_spacing": 0.05},
                          {"$type": "assign_flex_container",
                           "id": sphere_id,
                           "container_id": 0}
                          ])
        
        # Look a the pool for the passed-in "look" time. 
        for i in range(stim_time):
            # Look at the object.
            self.communicate({"$type": "look_at",
                              "avatar_id": "a",
                              "object_id":  self.pool_id,
                              "use_centroid": True})

        # Destroy the object and pause for the passed-in pause time.
        self.communicate({"$type": "destroy_object", "id": sphere_id})
        sleep(pause_time)

if __name__ == "__main__":
    FlexFluid().run()
