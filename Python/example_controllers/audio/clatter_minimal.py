from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.clatter import Clatter

"""
A minimal example of Clatter.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(c.get_add_physics_object(model_name="vase_02",
                                         position={"x": 0, "y": 3, "z": 0},
                                         object_id=c.get_unique_id()))
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 1, "y": 1, "z": -1},
                           look_at={"x": 0, "y": 0.5, "z": 0})
audio_initializer = ResonanceAudioInitializer(avatar_id="a")
clatter = Clatter(resonance_audio=True)
c.add_ons.extend([camera, audio_initializer, clatter])
c.communicate(commands)
for i in range(200):
    c.communicate([])
c.communicate({"$type": "terminate"})
