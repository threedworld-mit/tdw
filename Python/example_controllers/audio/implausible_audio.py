from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Generate audio using physics parameters that don't match the object's actual physics parameters.
"""


c = Controller()
floor_visual_material = "parquet_long_horizontal_clean"
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_material(material_name=floor_visual_material),
            {"$type": "set_floor_material",
             "name": floor_visual_material}]
object_id = c.get_unique_id()
model_name = "vase_02"
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         object_id=object_id,
                                         position={"x": 0, "y": 2, "z": 0}))
# Set random static audio data values.
object_audio = ClatterObject(fake_mass=30,
                             impact_material=ImpactMaterial.wood_soft,
                             amp=0.7,
                             resonance=0.1,
                             size=4)
# Add a listener.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1.6, "z": -2},
                           look_at={"x": 0, "y": 0.5, "z": 0})
# Initialize audio.
audio = AudioInitializer(avatar_id="a")
# Set a non-wood floor material.
floor_material = ImpactMaterial.metal
# Initialize Clatter.
clatter = Clatter(simulation_amp=0.9, objects={object_id: object_audio}, environment=floor_material)
# Add a recorder.
recorder = PhysicsAudioRecorder()
c.add_ons.extend([camera, audio, clatter, recorder])
# Create the scene.
c.communicate(commands)
# Start recording.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("implausible_audio/audio.wav")
print(f"Audio will be saved to: {path}")
if not path.parent.exists():
    path.parent.mkdir(parents=True)
recorder.start(path=path)
while not recorder.done:
    c.communicate([])
c.communicate({"$type": "terminate"})
