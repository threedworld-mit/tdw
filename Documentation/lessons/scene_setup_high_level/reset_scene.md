##### Scene Setup (High-Level APIs)

# Reset a scene

In general, the goal of resetting a scene is to revert the scene and its objects to an initial state. 

Resetting a scene is typically very fast because of how TDW manages [asset bundles](https://docs.unity3d.com/Manual/AssetBundlesIntro.html) in memory.

Object asset bundles stay in memory unless otherwise requested. This means that while the *first* time you add an object, it can take a long time to load, but adding subsequent copies of the object will be extremely fast. Even if an object is destroyed, its asset bundle will stay in memory.

Scene asset bundles are handled slightly differently: When a new scene is loaded, the previous scene is unloaded from memory.

Therefore, to reset a scene, there are two techniques in TDW that yield best results:

1. **Don't unload the scene unless you have to.** Group trials by scene. For example, if a trial can occur in one of six scenes, do trials per scene:

```python
from tdw.controller import Controller

class ResetScene(Controller):
    def do_trials(self, num_trials: int):
        scenes = ["tdw_room", "iceland_beach", "lava_field", "abandoned_factory"]
        # Divided the total number of trials by the number of scenes.
        num_trials_per_scene = int(num_trials / len(scenes))
        # Initialize a scene for the next batch of trials.
        for scene in scenes:
            self.communicate(self.get_add_scene(scene_name=scene))
            # Do trials for this scene.
            self.do_trials_in_scene(num_trials=num_trials_per_scene)
        self.communicate({"$type": "terminate"})
               
    def do_trials_in_scene(self, num_trials: int):
        for i in range(num_trials):
            # Your code here.
            pass


if __name__ == "__main__":
    c = ResetScene()
    c.do_trials(num_trials=10000)
```

2. **Destroy all objects in the scene with [`destroy_object`](../../api/command_api.md#destroy_object) or [`destroy_all_objects`](../../api/command_api.md#destroy_all_objects)**. `destroy_object` destroys a specific object and `destroy_all_objects` destroys all objects in the scene. You should also set the `"frequency"` of any ongoing output data commands such as [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies) to `"never"`; otherwise, they'll try to continue to send output data for non-existent objects.

   In the following example, an object is added to the scene above floor level and allowed to fall. The trial finishes when the object stops moving. Then the object is destroyed and the controller stops requesting output data:

```python
import numpy as np
from tdw.controller import Controller
from tdw.output_data import OutputData, Rigidbodies

class ResetScene(Controller):
    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    def do_trials(self, num_trials: int):
        scenes = ["tdw_room", "iceland_beach", "lava_field", "abandoned_factory"]
        # Divided the total number of trials by the number of scenes.
        num_trials_per_scene = int(num_trials / len(scenes))
        # Initialize a scene for the next batch of trials.
        for scene in scenes:
            self.communicate(self.get_add_scene(scene_name=scene))
            # Do trials for this scene.
            self.do_trials_in_scene(num_trials=num_trials_per_scene)
        self.communicate({"$type": "terminate"})

    def do_trials_in_scene(self, num_trials: int):
        for i in range(num_trials):
            # Add an object with a random rotation and starting height.
            object_id = self.get_unique_id()
            resp = self.communicate([self.get_add_object(model_name="rh10",
                                                         position={"x": 0, "y": self.rng.uniform(1.6, 3), "z": 0},
                                                         rotation={"x": self.rng.uniform(-360, 360),
                                                                   "y": self.rng.uniform(-360, 360),
                                                                   "z": self.rng.uniform(-360, 360)},
                                                         object_id=object_id),
                                     {"$type": "send_rigidbodies",
                                      "frequency": "always"}])

            done = False
            while not done:
                # Check if the object stopped moving.
                for j in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[j])
                    if r_id == "rigi":
                        rigidbodies = Rigidbodies(resp[j])
                        for k in range(rigidbodies.get_num()):
                            if rigidbodies.get_id(k) == object_id:
                                done = rigidbodies.get_sleeping(k)
                # Advance another frame.
                resp = self.communicate([])

            # Reset the scene by destroying the object.
            self.communicate([{"$type": "destroy_object",
                               "id": object_id},
                              {"$type": "send_rigidbodies",
                               "frequency": "never"}])


if __name__ == "__main__":
    c = ResetScene()
    c.do_trials(num_trials=10000)
```

3. **Reset your add-ons.** Some add-ons have a `reset()` function that should be called per scene reset. All add-ons have an `initialized` boolean; set this to False to re-initialize (though you should always opt for the `reset()` function if available because it will have useful parameters). [`Floorplan`](floorplans.md) and [`ProcGenKitchen`](proc_gen_kitchen.md) do *not* need to be reset; they are exceptions to the rule.

## Unloading asset bundles from memory

Model asset bundles can require a lot of memory. You can check the size of an asset bundle via `record.asset_bundle_sizes`:

```python
from tdw.librarian import ModelLibrarian

total_size = 0
lib = ModelLibrarian()
for record in lib.records:
    total_size += record.asset_bundle_sizes["Linux"]
print(total_size / (1 << 30), "GB")  # 1.5575027372688055 GB
```

[Other model libraries in TDW](../3d_models/overview.md) can be much larger than this: For example, the full model library is approximately 61 GB.

If your simulation includes many models, but not all at the same time, you might want to periodically unload model asset bundles from memory with the [`unload_asset_bundles` command](../../api/command_api.md#unload_asset_bundles). This will free up your machine's memory. However, the next time you create an object, the build will need to re-download and re-load the asset bundle back into memory.

## Reset a scene to an arbitrary state

Unfortunately, it isn't possible to reset to an arbitrary frame in the middle of a trial because Unity's physics engine isn't set up to allow "snapshots" of its current state. It's only possible to reset to an initial state, not a state during a trial.

***

**This is the last document in the "Scene Setup (High-Level APIs)" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [reset_scene.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/scene_setup_high_level/reset_scene.py) Create multiple trials of an object falling and reset the scene between trials.

Python API:

- [`ModelRecord.asset_bundle_sizes`](../../python/librarian/model_librarian.md) The size of each asset bundle per operating system.

Command API:

- [`destroy_object`](../../api/command_api.md#destroy_object)
- [`destroy_all_objects`](../../api/command_api.md#destroy_all_objects)
- [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies)
- [`unload_asset_bundles`](../../api/command_api.md#unload_asset_bundles)

Output Data API:

- [`Rigidbodies`](../../api/output_data.md#Rigidbodies)

