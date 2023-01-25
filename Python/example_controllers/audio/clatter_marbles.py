import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.physics_audio.impact_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION


c = Controller()
commands = [TDWUtils.create_empty_room(6, 6)]
# Get the audio values for each marble.
marble = ClatterObject(impact_material=ImpactMaterial.glass,
                       size=0,
                       amp=0.2,
                       resonance=0.05)
clatter_objects = dict()
# Add marbles in a grid at random heights.
extent = 0.4
diameter = 0.013
spacing = 0.1
marble_mass = 0.03
marble_bounciness = 0.6
marble_dynamic_friction = DYNAMIC_FRICTION[marble.impact_material]
marble_static_friction = STATIC_FRICTION[marble.impact_material]
object_id = 0
rng = np.random.RandomState()
z = -extent
while z < extent:
    x = -extent
    while x < extent:
        # Add the object.
        commands.extend(Controller.get_add_physics_object(model_name="sphere",
                                                          object_id=object_id,
                                                          library="models_flex.json",
                                                          position={"x": x, "y": float(1.8 + rng.uniform(0, 1)), "z": z},
                                                          default_physics_values=False,
                                                          scale_factor={"x": diameter, "y": diameter, "z": diameter},
                                                          mass=marble_mass,
                                                          bounciness=marble_bounciness,
                                                          static_friction=marble_static_friction,
                                                          dynamic_friction=marble_dynamic_friction))
        # Set a random color.
        commands.append({"$type": "set_color",
                         "id": object_id,
                         "color": {"r": float(rng.uniform(0, 1)),
                                   "g": float(rng.uniform(0, 1)),
                                   "b": float(rng.uniform(0, 1)),
                                   "a": 1.0}})
        # Remember the marble Clatter data.
        clatter_objects[object_id] = marble
        # Increment the object ID.
        object_id += 1
        x += spacing
    z += spacing
# Create the camera.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1, "z": -1},
                           look_at={"x": 0, "y": 0.5, "z": 0})
# Initialize audio.
audio = AudioInitializer(avatar_id=camera.avatar_id)
# Create the Clatter add-on. Add the object data overrides and set the environment parameters.
clatter = Clatter(objects=clatter_objects,
                  environment=ClatterObject(impact_material=ImpactMaterial.metal,
                                            size=4,
                                            amp=0.5,
                                            resonance=0.4,
                                            fake_mass=100))
# Add the add-ons.
c.add_ons.extend([camera, audio, clatter])
# Send the commands.
c.communicate(commands)
# Let the marbles fall.
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
