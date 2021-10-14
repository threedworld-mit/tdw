from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Simple example of using PyImpact and PhysicsAudioRecorder to generate and record audio.
"""

c = Controller()
commands = [TDWUtils.create_empty_room(12, 12)]
table_id = c.get_unique_id()
commands.extend(c.get_add_physics_object(model_name="small_table_green_marble",
                                         object_id=table_id,
                                         scale_factor={"x": 5, "y": 0.1, "z": 5}))
object_id = c.get_unique_id()
model_name = "octahedron"
object_mass = 5
object_bounciness = 0.5
avatar_id = "a"
color = {"r": 0.8, "g": 0.1, "b": 0.5, "a": 1}
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         library="models_flex.json",
                                         object_id=object_id,
                                         scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                         position={"x": 0, "y": 1.5, "z": -1},
                                         rotation={"x": 30, "y": 27, "z": 0},
                                         default_physics_values=False,
                                         mass=object_mass,
                                         bounciness=object_bounciness))
commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 5, "z": -1.1},
                                       look_at={"x": 0, "y": 0, "z": 0},
                                       avatar_id=avatar_id))
commands.extend([{"$type": "apply_torque_to_object",
                  "id": object_id,
                  "torque": {"x": -45, "y": 20, "z": 1}},
                 {"$type": "apply_force_to_object",
                  "id": object_id,
                  "force": {"x": 0, "y": 0, "z": 20}},
                 {"$type": "set_color",
                  "id": object_id,
                  "color": color}])
floor_material = "tile"
audio_initializer = ResonanceAudioInitializer(avatar_id=avatar_id, floor=floor_material)
py_impact = PyImpact(initial_amp=0.9,
                     resonance_audio=True,
                     floor=ResonanceAudioInitializer.AUDIO_MATERIALS[floor_material],
                     static_audio_data_overrides={model_name: ObjectAudioStatic(name=model_name,
                                                                                object_id=object_id,
                                                                                material=AudioMaterial.metal,
                                                                                mass=object_mass,
                                                                                bounciness=object_bounciness,
                                                                                amp=0.8,
                                                                                resonance=0.7,
                                                                                size=1)})
recorder = PhysicsAudioRecorder()
root_dir = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("py_impact")
path = root_dir.joinpath("impact.wav")
c.add_ons.extend([audio_initializer, py_impact, recorder])
c.communicate(commands)
recorder.start(output_path=path)
while recorder.recording:
    c.communicate([])

# Scrape trial.
py_impact.reset()
commands = [{"$type": "destroy_object",
             "id": object_id}]
object_id = c.get_unique_id()
model_name = "cube"
commands.extend(c.get_add_physics_object(model_name=model_name,
                                         library="models_flex.json",
                                         object_id=object_id,
                                         scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                                         default_physics_values=False,
                                         mass=object_mass,
                                         bounciness=object_bounciness))
commands.extend([{"$type": "apply_force_to_object",
                  "id": object_id,
                  "force": {"x": 0, "y": 0, "z": 30}},
                 {"$type": "set_color",
                  "id": object_id,
                  "color": color}])
path = root_dir.joinpath("scrape.wav")
c.communicate(commands)
recorder.start(output_path=path)
while recorder.recording:
    c.communicate([])
c.communicate({"$type": "terminate"})
