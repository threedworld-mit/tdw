##### Clatter

# Clatter and Resonance Audio

Clatter can be used with [Resonance Audio](../audio/resonance_audio.md). The setup process is the same as using Resonance Audio in other contexts, with two extra steps:

1. In the `Clatter` add-on constructor, you must set `resonance_audio=True`
2. You may want to set `environment` in the `Clatter` constructor to match the `floor` in the `ResonanceAudioInitializer` constructor. Resonance Audio materials are not the same as `ImpactMaterial` values but `ResonanceAudioInitializer` provides a dictionary mapping one to the other:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.physics_audio.impact_material import ImpactMaterial

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
```

***

**Next: [Reset Clatter](reset.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [resonance_audio.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/clatter/resonance_audio.py) A minimal example of Clatter using Resonance Audio.

Python API:

- [`ResonanceAudioInitializer`](../../python/add_ons/resonance_audio_initializer.md)
- [`Clatter`](../../python/add_ons/clatter.md)

