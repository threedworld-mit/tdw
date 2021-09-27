import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.third_person_camera import ThirdPersonCamera

"""
Drop an object with varying physics values and observe its behavior.
"""

c = Controller()
c.communicate(TDWUtils.create_empty_room(12, 12))

# Do a number of trials.
num_trials = 10

# Set the 0 to another number to use a different random seed.
rng = np.random.RandomState(0)

# Add a camera and an object manager.
camera = ThirdPersonCamera(position={"x": 3, "y": 2.5, "z": -1},
                           look_at={"x": 0, "y": 0, "z": 0})
object_manager = ObjectManager(transforms=True, rigidbodies=True)
c.add_ons.extend([camera, object_manager])

# Run the trials.
for i in range(10):
    object_id = c.get_unique_id()
    # Add the object.
    c.communicate(c.get_add_physics_object(model_name="iron_box",
                                           object_id=object_id,
                                           position={"x": 0, "y": 7, "z": 0},
                                           default_physics_values=False,
                                           mass=float(rng.uniform(0.5, 6)),
                                           dynamic_friction=float(rng.uniform(0, 1)),
                                           static_friction=float(rng.uniform(0, 1)),
                                           bounciness=float(rng.uniform(0, 1))))
    done = False
    while not done:
        c.communicate([])
        done = object_manager.rigidbodies[object_id].sleeping
    # Destroy the object.
    c.communicate({"$type": "destroy_object",
                   "id": object_id})
    # Mark the object manager as requiring re-initialization.
    object_manager.initialized = False
c.communicate({"$type": "terminate"})
