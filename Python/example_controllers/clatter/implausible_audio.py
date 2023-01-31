from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.clatter_object import ClatterObject

"""
Generate implausible audio.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
object_id = c.get_unique_id()
model_name = "vase_02"
clatter_object = ClatterObject(impact_material=ImpactMaterial.wood_soft,
                               amp=0.1,
                               resonance=0.1,
                               size=4,
                               fake_mass=100)
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         object_id=object_id,
                                         position={"x": 0, "y": 2, "z": 0},
                                         default_physics_values=False,
                                         dynamic_friction=0.2,
                                         static_friction=0.3,
                                         bounciness=0.9,
                                         mass=1))
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1.6, "z": -2},
                           look_at={"x": 0, "y": 0.5, "z": 0})
audio = AudioInitializer(avatar_id="a")
clatter = Clatter(simulation_amp=0.9, objects={object_id: clatter_object})
c.add_ons.extend([camera, audio, clatter])
# Create the scene.
c.communicate(commands)
for i in range(150):
    c.communicate([])
c.communicate({"$type": "terminate"})
