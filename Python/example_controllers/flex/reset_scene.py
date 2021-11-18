import numpy as np
from typing import Tuple, List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, FlexParticles
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ResetScene(Controller):
    """
    Minimal example of how to reset a Flex scene.
    """

    def trial(self, model_name: str, mass: float, height: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Drop an Flex object and record its particles.
        """

        object_id = c.get_unique_id()
        resp = self.communicate([{"$type": "create_flex_container"},
                                 c.get_add_object(model_name=model_name,
                                                  library="models_flex.json",
                                                  object_id=object_id,
                                                  position={"x": 0, "y": height, "z": 0}),
                                 {"$type": "set_flex_soft_actor",
                                  "id": object_id,
                                  'particle_spacing': 0.125,
                                  'cluster_stiffness': 0.5,
                                  "mass_scale": mass},
                                 {"$type": "assign_flex_container",
                                  "id": object_id,
                                  "container_id": 0},
                                 {"$type": "send_flex_particles",
                                  "frequency": "always"}])
        particles: List[np.ndarray] = list()
        velocities: List[np.ndarray] = list()
        # Let the object fall.
        for i in range(250):
            for j in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[j])
                # Log the particle data on this frame.
                if r_id == "flex":
                    flex = FlexParticles(resp[j])
                    for k in range(flex.get_num_objects()):
                        if flex.get_id(k) == object_id:
                            particles.append(flex.get_particles(k))
                            velocities.append(flex.get_velocities(k))
            resp = self.communicate([])
        # Reset the scene.
        self.communicate([{"$type": "destroy_flex_object",
                           "id": object_id},
                          {"$type": "destroy_flex_container",
                           "id": 0}])
        return np.array(particles), np.array(velocities)

    def run(self) -> None:
        """
        Run a series of trials.
        """

        output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("reset_flex_scene")
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        print(f"Particle data will be saved to: {output_directory}")
        # Create the scene.
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "convexify_proc_gen_room"}])
        i = 0
        for model_name, height, mass in zip(["cube", "octahedron", "dumbbell"],
                                            [1, 1.5, 1.78],
                                            [5, 6, 2]):
            particles, velocities = self.trial(model_name=model_name, height=height, mass=mass)
            # Save the particle data.
            np.save(str(output_directory.joinpath(f"particles_{i}").resolve()), np.array(particles))
            np.save(str(output_directory.joinpath(f"velocities_{i}").resolve()), np.array(velocities))
            i += 1
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ResetScene()
    c.run()
