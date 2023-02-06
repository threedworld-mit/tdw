##### Clatter

# Clatter and Resonance Audio

To reset Clatter, call `clatter.reset()`.

`reset()` has two optional parameters:

- `random_seed` which can optionally hardcode the random seed.
- `objects` which is the same as the `objects` parameter in the constructor. When you call `reset()`, the current user-defined dictionary of `ClatterObject` data is cleared and must be reassigned. [Read this for more information.](clatter_objects.md)

As with the initial Clatter constructor call, for best results  you should call `clatter.reset()` on the same communicate() call as when all objects are added to the scene.

This is a minimal example of how to reset Clatter:

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.impact_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION


class ResetClatter(Controller):
    """
    Reset `Clatter` between trials.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(0)

        # Add a camera.
        camera = ThirdPersonCamera(position={"x": 1, "y": 1.7, "z": -0.5},
                                   look_at={"x": 0, "y": 0.5, "z": 0},
                                   avatar_id="a")
        floor = ImpactMaterial.wood_medium
        # Initialize audio.
        audio_initializer = ResonanceAudioInitializer(avatar_id="a", 
                                                      floor=ResonanceAudioInitializer.RESONANCE_AUDIO_MATERIALS[floor])
        # Initialize Clatter, using the controller's RNG.
        self.clatter = Clatter(simulation_amp=0.5,
                               environment=floor,
                               random_seed=0,
                               resonance_audio=True,)
        # Initialize the scene.
        self.add_ons.extend([camera, audio_initializer, self.clatter])
        self.communicate(TDWUtils.create_empty_room(7, 7))

    def trial(self) -> None:
        # Set the parameters for initializing the object.
        object_id: int = self.get_unique_id()
        object_name: str = "vase_02"
        object_mass: float = float(self.rng.uniform(0.5, 0.8))
        object_bounciness: float = float(self.rng.uniform(0.5, 0.7))
        object_material = ImpactMaterial.wood_soft
        clatter_object = ClatterObject(impact_material=object_material,
                                       size=1,
                                       amp=0.6,
                                       resonance=0.45)
        # Reset Clatter.
        self.clatter.reset(objects={object_id: clatter_object})
        # Add the object.
        self.communicate(self.get_add_physics_object(model_name=object_name,
                                                     position={"x": 0, "y": float(self.rng.uniform(3, 4)), "z": 0},
                                                     object_id=object_id,
                                                     default_physics_values=False,
                                                     mass=object_mass,
                                                     dynamic_friction=DYNAMIC_FRICTION[object_material],
                                                     static_friction=STATIC_FRICTION[object_material],
                                                     bounciness=object_bounciness))
        # Let the object fall.
        for i in range(200):
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})

    def run(self) -> None:
        for i in range(10):
            self.trial()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = ResetClatter()
    c.run()
```

***

**Next: [Manually generate audio (Clatter CLI)](cli.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [reset_clatter.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/reset_clatter.py) A minimal example of how to reset Clatter.

Python API:

- [`ResonanceAudioInitializer`](../../python/add_ons/resonance_audio_initializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)