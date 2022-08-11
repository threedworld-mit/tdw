##### Physics (Flex)

# Reset a Flex scene

*Many of the techniques involved in resetting a non-Flex scene are the same as those for non-Flex TDW scenes. The main difference is which commands you need to send. If you haven't done so already, [read this document regarding resetting a scene.](../scene_setup_high_level/reset_scene.md)*

When resetting a Flex scene, be sure to clear Flex data from memory. [Flex always leaks memory during a scene reset](flex.md) but these commands will leak much less memory:

- For each Flex object, you must send [`destroy_flex_object`](../../api/command_api.md#destroy_flex_object). Send this *instead* of [`destroy_object`](../../api/command_api.md#destroy_object) for Flex. Send this even if you are unloading and reloading a scene. 
- After destroying all Flex objects in the scene, destroy all Flex containers with [`destroy_flex_container`](../../api/command_api.md#destroy_flex_container).  Send this even if you are unloading and reloading a scene. 

This minimal example correctly resets a Flex scene. It runs a series of trials in which an object is dropped from a given height. After each trial, the controller saves the particle data as a .npy file and resets the scene:

```python
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
```

***

**Next: [Other Flex commands](other_commands.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [reset_scene.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/flex/reset_scene.py) Minimal example of how to reset a Flex scene.

Command API:

- [`destroy_flex_object`](../../api/command_api.md#destroy_flex_object)
- [`destroy_object`](../../api/command_api.md#destroy_flex_object)
- [`destroy_flex_container`](../../api/command_api.md#destroy_flex_container)