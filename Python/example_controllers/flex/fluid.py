import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.flex_data.fluid_type import FLUID_TYPES


class FlexFluids(Controller):
    """
    Generate fluid simulation trials with random fluids.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Create a scene and add a camera.
        commands = [self.get_add_scene(scene_name="tdw_room")]
        commands.extend(TDWUtils.create_avatar(position={"x": -3.75, "y": 1.5, "z": -0.5},
                                               look_at={"x": 0, "y": 0, "z": 0},
                                               avatar_id="a"))
        self.communicate(commands)

    def trial(self, fluid_name: str) -> None:
        fluid = FLUID_TYPES[fluid_name]
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
                          {"$type": "set_flex_fluid_actor",
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
            fluid_keys = list(FLUID_TYPES.keys())
            fluid_name = random.choice(fluid_keys)
            self.trial(fluid_name=fluid_name)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = FlexFluids()
    c.run(num_trials=15)
