##### Audio

# Resonance Audio

**Resonance Audio** is TDW's advanced audio system. Resonance audio supports:

- Advanced audio spatialization
- Audio occlusion, i.e. a wall between the audio source and the listener will affect the output.
- Physics-based reverb. The floor, ceiling, and walls each have "resonance audio materials" 
- Objects in the system will affect the audio. In other words, an object dropped in an empty room will sound very different than an object dropped in a room populated by many objects.

Resonance Audio is best used with interior room environments.

Resonance Audio has the same [system requirements](initialize_audio.md) as Unity's built-in audio system.

## Initialize a scene with Resonance Audio

Initializing a scene with Resonance Audio is very similar to initializing a scene with the built-in audio system. You need to:

1. [Initialize the scene](../core_concepts/scenes.md)
2. [Add an avatar](../core_concepts/avatars.md)
3. Add an **Resonance Audio sensor** to the avatar

The final step can be simplified with the [`ResonanceAudioInitializer` add-on](../../python/add_ons/resonance_audio_initializer.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer

c = Controller()
audio_initializer = ResonanceAudioInitializer(avatar_id="a", framerate=60)
c.add_ons.append(audio_initializer)
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="a"))
c.communicate(commands)
```

You can do the exact same thing with a [`ThirdPersonCamera` add-on](../../python/add_ons/third_person_camera.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
audio_initializer = AudioInitializer(avatar_id="a", framerate=60)
camera = ThirdPersonCamera(avatar_id="a")
# Note the order: The camera must be added before audio is initialized.
c.add_ons.extend([camera, audio_initializer])
c.communicate(TDWUtils.create_empty_room(12, 12))
```

Resonance Audio creates a "reverb space" is a box-shaped volume. By default, it matches the total size of the scene environment (in this case, 12x12 meters). 

The floor, ceiling, and individual walls of the reverb space have "audio materials" that will affect audio output. The following materials are available:

```
roughPlaster
tile
concrete
wood
smoothPlaster
acousticTile
glass
parquet
marble
grass
brick
metal
```

By default, the floor is `parquet`, the ceiling is `acousticTile`, and the walls are all `smoothPlaster`.

To set the reverb space audio materials, set the values of the optional parameters of the `ResonanceAudioInitializer` constructor:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
audio_initializer = ResonanceAudioInitializer(avatar_id="a",
                                              framerate=60,
                                              floor="tile",
                                              ceiling="brick",
                                              front_wall="concrete",
                                              back_wall="smoothPlaster",
                                              left_wall="metal",
                                              right_wall="metal",
                                              region_id=-1)
camera = ThirdPersonCamera(avatar_id="a")
# Note the order: The camera must be added before audio is initialized.
c.add_ons.extend([camera, audio_initializer])
c.communicate(TDWUtils.create_empty_room(12, 12))
```

Or you can set up Resonance Audio with low-level commands:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera


c = Controller()
camera = ThirdPersonCamera(avatar_id="a")
c.add_ons.append(camera)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "set_reverb_space_simple", 
                "region_id": -1,
                "reverb_floor_material": "tile",
                "reverb_ceiling_material": "brick", 
                "reverb_front_wall_material": "concrete",
                "reverb_back_wall_material": "smoothPlaster",
                "reverb_left_wall_material": "metal",
                "reverb_right_wall_material": "metal"},
               {"$type": "set_target_framerate", 
                "framerate": 60},
               {"$type": "add_environ_audio_sensor", 
                "avatar_id": "a"}])
```

##  The `region_id` parameter

The `region_id` parameter controls the position and size of the reverb space. In some scenes, it's possible to have multiple reverb spaces.

If `region_id` is set to -1, then the reverb space will be the size of the scene. The default value of `region_id` in both `ResonanceAudioInitializer` and the underlying [`set_reverb_space_simple`](../../api/command_api.md#set_reverb_space_simple) command is -1.

Certain [streamed scenes](../core_concepts/scenes.md) have multiple *scene regions*. In interior scenes, scene regions are usually individual *rooms*. Each region has an ID. Set `region_id` to this value to create a reverb space that matches the position and size of the scene region.

```python
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.scene_data.scene_bounds import SceneBounds


c = Controller()
camera = ThirdPersonCamera(avatar_id="a")
c.add_ons.append(camera)
resp = c.communicate([c.get_add_scene(scene_name="tdw_room"),
                      {"$type": "send_scene_regions"}])
scene_bounds = SceneBounds(resp)
region_id = scene_bounds.rooms[0].region_id
audio_initializer = ResonanceAudioInitializer(avatar_id="a",
                                              region_id=region_id)
c.add_ons.append(audio_initializer)
c.communicate([])
```

## Play audio

You can call `audio_intializer.play(path, position)` to play a .wav file. 

- `path` is the path to the .wav file
- `position` is the position of the audio source. 
- You can optionally set the parameter `audio_id`. Each audio source has a unique ID. If you don't set this parameter, a unique ID will be generated.
- You can optionally set the parameter `object_id`. If you do, the audio source will be parented to the corresponding object such that whenever the object moves, the source will move with it. Internally, this is handled with via the command [`parent_audio_source_to_object`](../../api/command_api.md#parent_audio_source_to_object).

This `play()` function loads the .wav file and converts it into a useable byte array. It then tells the build to play the audio by sending [`play_point_source_data`](../../api/command_api.md#play_point_source_data).

This controller will create a scene and initialize audio. It will then play two audio clips. While the audio is playing,  it will be repositioned in order to demonstrate the Resonance Audio effects. The audio clips can be found [here](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio).

```python
from typing import Dict
from time import sleep
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer


class Audio(Controller):
    """
    Create a scene with a reverb space and audio sensor. Test how object positions can affect reverb.
    """

    def delay_and_teleport(self, id_0: int, id_1: int, pos_0: Dict[str, float], pos_1: Dict[str, float]) -> None:
        """
        Wait ten seconds and then teleport the objects.

        :param id_0: The ID of the first object.
        :param id_1: The ID of the second object.
        :param pos_0: The new position of the first object.
        :param pos_1: The new position of the second object.
        """
        
        sleep(10)
        self.communicate([{"$type": "teleport_object",
                           "id": id_0,
                           "position": pos_0},
                          {"$type": "teleport_object",
                           "id": id_1,
                           "position": pos_1}])

    def run(self) -> None:
        pos_0 = {"x": 3.16, "y": 0, "z": 4.34}
        pos_1 = {"x": -2.13, "y": 0, "z": -1.0}
        pos_2 = {"x": -1.9, "y": 0, "z": 1.45}
        pos_3 = {"x": 2.4, "y": 0, "z": -4.3}
        pos_4 = {"x": 0, "y": 0, "z": 0}

        object_id_0 = self.get_unique_id()
        object_id_1 = self.get_unique_id()
        audio_id_0 = self.get_unique_id()
        audio_id_1 = self.get_unique_id()

        # Add a camera.
        camera = ThirdPersonCamera(position={"x": -4, "y": 1.5, "z": 0},
                                   look_at={"x": 2.5, "y": 0, "z": 0},
                                   avatar_id="a",
                                   fov=75)
        # Enable Resonance Audio.
        audio = ResonanceAudioInitializer(avatar_id="a",
                                          floor="marble")
        self.add_ons.extend([camera, audio])

        # Load the scene.
        # Add two objects. Make both objects kinematic.
        self.communicate([self.get_add_scene(scene_name="tdw_room"),
                          self.get_add_object(model_name="satiro_sculpture",
                                              position=pos_0,
                                              rotation={"x": 0.0, "y": -108, "z": 0.0},
                                              library="models_core.json",
                                              object_id=object_id_0),
                          self.get_add_object(model_name="buddah",
                                              position=pos_1,
                                              rotation={"x": 0.0, "y": 90, "z": 0.0},
                                              library="models_core.json",
                                              object_id=object_id_1),
                          {"$type": "set_kinematic_state",
                           "id": object_id_0,
                           "is_kinematic": True,
                           "use_gravity": False},
                          {"$type": "set_kinematic_state",
                           "id": object_id_1,
                           "is_kinematic": True,
                           "use_gravity": False}])
        # Start to play audio on both objects.
        # Parent each audio source to its corresponding object.
        audio.play(path="HWL_1b.wav",
                   audio_id=audio_id_0,
                   object_id=object_id_0,
                   position={"x": pos_0["x"], "y": pos_0["y"] + 0.85, "z": pos_0["z"]})
        audio.play(path="HWL_3c.wav",
                   audio_id=audio_id_1,
                   object_id=object_id_1,
                   position={"x": pos_1["x"], "y": pos_1["y"] + 0.85, "z": pos_1["z"]})
        self.communicate([])

        # Every ten seconds, adjust the positions of the objects.
        self.delay_and_teleport(object_id_0, object_id_1, pos_1, pos_0)
        self.delay_and_teleport(object_id_0, object_id_1, pos_2, pos_3)
        self.delay_and_teleport(object_id_0, object_id_1, pos_3, pos_2)
        self.delay_and_teleport(object_id_0, object_id_1, pos_2, pos_4)
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    Audio().run()
```

## The `set_reverb_space_expert` command

TDW includes an additional command to create a reverb space: [`set_reverb_space_expert`](../../api/command_api.md#set_reverb_space_expert). This command is not included in the `ResonanceAudioInitializer` add-on and includes additional parameters for fine-tuning the scene's audio.

***

**Next: [`PyImpact` (dynamic impact sounds)](py_impact.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [resonance_audio.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/audio/resonance_audio.py) Initialize and play Resonance Audio.

Python API:

- [`ResonanceAudioInitializer`](../../python/add_ons/resonance_audio_initializer.md)
- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)
- [`SceneBounds`](../../python/scene_data/scene_bounds.md)

Command API:

- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)
- [`set_reverb_space_simple`](../../api/command_api.md#set_reverb_space_simple)
- [`add_environ_audio_sensor`](../../api/command_api.md#add_environ_audio_sensor)
- [`send_scene_regions`](../../api/command_api.md#send_scene_regions)
- [`parent_audio_source_to_object`](../../api/command_api.md#parent_audio_source_to_object)
- [`play_point_source_data`](../../api/command_api.md#play_point_source_data)
- [`set_kinematic_state`](../../api/command_api.md#set_kinematic_state)
- [`set_reverb_space_expert`](../../api/command_api.md#set_reverb_space_expert)

Output Data:

- [`SceneRegions`](../../api/output_data.md#SceneRegions)

