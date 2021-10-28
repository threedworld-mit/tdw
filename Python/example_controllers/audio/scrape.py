from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.physics_audio.object_audio_static import ObjectAudioStatic
from tdw.physics_audio.audio_material import AudioMaterial
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

""":field
Record scrape sounds.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 1.3, "y": 2.1, "z": -1.1},
                           look_at={"x": 0, "y": 0.5, "z": 0},
                           avatar_id="a")
audio = AudioInitializer(avatar_id="a")
py_impact = PyImpact()
recorder = PhysicsAudioRecorder()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape")
print(f"Audio will be saved to: {path}")
c.add_ons.extend([camera, audio, py_impact, recorder])
c.communicate(TDWUtils.create_empty_room(12, 12))
lib_core = ModelLibrarian("models_core.json")
lib_flex = ModelLibrarian("models_flex.json")
cube_mass = 10
cube_bounciness = 0.4
for scrape_surface_model_name in ["glass_table", "quatre_dining_table", "small_table_green_marble"]:
    surface_record = lib_core.get_record(scrape_surface_model_name)
    for audio_material in [AudioMaterial.wood_medium, AudioMaterial.ceramic, AudioMaterial.metal]:
        # Add the surface.
        surface_id = c.get_unique_id()
        cube_id = c.get_unique_id()
        commands = c.get_add_physics_object(model_name=scrape_surface_model_name,
                                            library="models_core.json",
                                            object_id=surface_id,
                                            kinematic=True)
        # Add the cube just above the top of the surface.
        commands.extend(c.get_add_physics_object(model_name="cube",
                                                 library="models_flex.json",
                                                 object_id=cube_id,
                                                 position={"x": 0, "y": surface_record.bounds["top"]["y"], "z": 0},
                                                 scale_factor={"x": 0.1, "y": 0.1, "z": 0.1},
                                                 default_physics_values=False,
                                                 mass=cube_mass,
                                                 dynamic_friction=0.2,
                                                 static_friction=0.2,
                                                 bounciness=cube_bounciness))
        # Define audio for the cube.
        cube_audio = ObjectAudioStatic(name="cube",
                                       object_id=cube_id,
                                       mass=cube_mass,
                                       bounciness=cube_bounciness,
                                       amp=0.2,
                                       resonance=0.45,
                                       size=1,
                                       material=audio_material)
        # Reset PyImpact.
        py_impact.reset(static_audio_data_overrides={cube_id: cube_audio}, initial_amp=0.9)
        c.communicate(commands)
        recorder.start(path=path.joinpath(f"{scrape_surface_model_name}_{audio_material.name}.wav"))
        # Apply a lateral force to start scraping.
        c.communicate({"$type": "apply_force_magnitude_to_object",
                       "magnitude": 12,
                       "id": cube_id})
        while recorder.recording:
            c.communicate([])
        # Destroy the objects to reset the scene.
        c.communicate([{"$type": "destroy_object",
                        "id": cube_id},
                       {"$type": "destroy_object",
                        "id": surface_id}])
c.communicate({"$type": "terminate"})
