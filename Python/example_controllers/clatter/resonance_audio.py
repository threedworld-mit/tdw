from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.impact_material import ImpactMaterial

"""
A minimal example of Clatter using Resonance Audio.
"""

c = Controller()
floor_visual_material = "parquet_wood_mahogany"
commands = [TDWUtils.create_empty_room(12, 12),
            Controller.get_add_material(material_name=floor_visual_material),
            {"$type": "set_floor_material",
             "name": floor_visual_material}]
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1, "z": -1},
                           look_at={"x": 0, "y": 0.5, "z": 0})
floor = ImpactMaterial.wood_medium
audio_initializer = ResonanceAudioInitializer(avatar_id="a",
                                              floor=ResonanceAudioInitializer.RESONANCE_AUDIO_MATERIALS[floor])
clatter = Clatter(resonance_audio=True,
                  environment=floor)
c.add_ons.extend([camera, audio_initializer, clatter])
c.communicate(commands)
for i in range(100):
    c.communicate([])
c.communicate({"$type": "terminate"})
