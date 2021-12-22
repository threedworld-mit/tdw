import numpy as np
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

c = Controller(launch_build=True)
# Camera for first and second sequence
camera = ThirdPersonCamera(position={"x": 1.0, "y": 1.27, "z": -1.66},
# Camera for third sequence
#camera = ThirdPersonCamera(position={"x": 1.0, "y": 1.27, "z": -1.66},
                           look_at={"x": 0, "y": 0.5, "z": 0},
                           avatar_id="a")
audio = AudioInitializer(avatar_id="a")

# Set a random number generator with a hardcoded random seed so that the generated audio will always be the same.
# If you want the audio to change every time you run the controller, do this instead: `py_impact = PyImpact()`.
rng = np.random.RandomState(0)
py_impact = PyImpact(rng=rng)

recorder = PhysicsAudioRecorder()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape")
print(f"Audio will be saved to: {path}")
c.add_ons.extend([camera, audio, py_impact, recorder])
c.communicate(c.get_add_scene(scene_name="tdw_room"))
c.communicate({"$type": "rotate_directional_light_by", "angle": -10, "axis": "pitch", "index": 0})
lib_core = ModelLibrarian("models_core.json")
lib_flex = ModelLibrarian("models_flex.json")
#cube_mass = 1.0
cube_bounciness = 0.4
for scrape_surface_model_name, surface_audio_material, surface_reso, surface_friction in zip(["glass_table", "quatre_dining_table", "small_table_green_marble"],
                                                                                             [AudioMaterial.glass, AudioMaterial.plastic_hard, AudioMaterial.ceramic],
                                                                                             [0.65, 0.3, 0.25],
                                                                                             [0.35, 0.5, 0.47]):
    surface_record = lib_core.get_record(scrape_surface_model_name)
    # Add the surface.
    surface_id = c.get_unique_id()
    commands = c.get_add_physics_object(model_name=scrape_surface_model_name,
                                        library="models_core.json",
                                        object_id=surface_id,
                                        dynamic_friction=surface_friction,
                                        static_friction=surface_friction,
                                        default_physics_values=False,
                                        kinematic=True)
    if scrape_surface_model_name == "glass_table":
        commands.append({"$type": "rotate_object_by", 
                         "angle": 90.0, 
                         "id": surface_id, 
                         "axis": "yaw"})
    c.communicate(commands)
    for cube_audio_material, cube_visual_material, object_name, object_mass, object_id, object_scale, object_reso, object_friction in zip([AudioMaterial.wood_medium, AudioMaterial.ceramic, AudioMaterial.metal],
                                                                                                                                       ["wood_beech_natural", "ceramic_porcelain", "chrome"],
                                                                                                                                       ["t-shape_wood_block", "plate05", "9v_battery"],
                                                                                                                                       [1.0, 1.0, 0.7],
                                                                                                                                       [777, 888, 999],
                                                                                                                                       [{"x": 1.5, "y": 1.5, "z": 1.5}, {"x": 1.25, "y": 1.25, "z": 1.25}, {"x": 1.0, "y": 1.0, "z": 1.0}],
                                                                                                                                       [0.2, 0.3, 0.2],
                                                                                                                                       [0.35, 0.5, 0.75]):
        for force in [0.75, 1.0, 1.5, 1.75, 2.25, 2.75, 3.25, 3.75]:
            cube_id = c.get_unique_id()
            # Add the cube just above the top of the surface.
            commands=c.get_add_physics_object(model_name=object_name,
                                              library="models_full.json",
                                              object_id=object_id,
                                              position={"x": 0,
                                                         "y": surface_record.bounds["top"]["y"] + 0.05,
                                                         "z": surface_record.bounds["back"]["z"] + 0.1},
                                              scale_factor=object_scale,
                                              default_physics_values=False,
                                              mass=object_mass,
                                              dynamic_friction=object_friction,
                                              static_friction=object_friction,
                                              bounciness=cube_bounciness)
            commands.extend([c.get_add_material(cube_visual_material, library="materials_med.json"),
                             {"$type": "set_visual_material",
                              "id": object_id,
                              "material_name": cube_visual_material,
                              "object_name": object_name,
                              "material_index": 0},
                             {"$type": "set_aperture", "aperture": 8.0},
                             {"$type": "set_field_of_view", "field_of_view": 60, "avatar_id": "a"},
                             {"$type": "set_shadow_strength", "strength": 1.0},
                             {"$type": "set_screen_size", "width": 1920, "height": 1080}])
            # Define audio for the cube.
            cube_audio = ObjectAudioStatic(name=object_name,
                                           object_id=object_id,
                                           mass=object_mass,
                                           bounciness=cube_bounciness,
                                           amp=0.2,
                                           resonance=object_reso,
                                           size=1,
                                           material=cube_audio_material)

            # Define audio for the surface.
            surface_audio = ObjectAudioStatic(name=scrape_surface_model_name,
                                           object_id=surface_id,
                                           mass=5,
                                           bounciness=0.25,
                                           amp=0.2,
                                           resonance=surface_reso,
                                           size=4,
                                           material=surface_audio_material)
            # Reset PyImpact.
            py_impact.reset(static_audio_data_overrides={cube_id: cube_audio, surface_id: surface_audio}, initial_amp=0.9)
            c.communicate(commands)
            recorder.start(path=path.joinpath(f"{scrape_surface_model_name}_{cube_audio_material.name}_{force}.wav"))
            # Apply a lateral force to start scraping.
            c.communicate({"$type": "apply_force_magnitude_to_object",
                           "magnitude": force,
                           "id": object_id})
            while recorder.recording:
                c.communicate([])
            # Destroy the objects.
            c.communicate({"$type": "destroy_object",
                            "id": object_id})
        # Destroy the surface.
    c.communicate({"$type": "destroy_object",
                   "id": surface_id})

c.communicate({"$type": "terminate"})
