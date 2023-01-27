from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

""":field
Record scrape sounds.
"""

c = Controller()
camera = ThirdPersonCamera(position={"x": 1.3, "y": 2.1, "z": -1.1},
                           look_at={"x": 0, "y": 0.5, "z": 0},
                           avatar_id="a")
audio = AudioInitializer(avatar_id="a")
# Initialized Clatter with a hardcoded random seed.
clatter = Clatter(random_seed=0)
recorder = PhysicsAudioRecorder()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape")
print(f"Audio will be saved to: {path}")
c.add_ons.extend([camera, audio, clatter, recorder])
c.communicate(TDWUtils.create_empty_room(12, 12))
lib_core = ModelLibrarian("models_core.json")
lib_flex = ModelLibrarian("models_flex.json")
cube_mass = 1
cube_bounciness = 0.4
for scrape_surface_model_name in ["quatre_dining_table", "small_table_green_marble"]:
    surface_record = lib_core.get_record(scrape_surface_model_name)
    for cube_audio_material, cube_visual_material in zip([ImpactMaterial.wood_medium, ImpactMaterial.ceramic, ImpactMaterial.metal],
                                                         ["wood_beech_natural", "ceramic_raw_striped", "metal_cast_iron"]):
        for force in [0.5, 1, 1.5, 3.5]:
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
                                                     position={"x": 0,
                                                               "y": surface_record.bounds["top"]["y"],
                                                               "z": surface_record.bounds["back"]["z"] + 0.1},
                                                     scale_factor={"x": 0.1, "y": 0.1, "z": 0.1},
                                                     default_physics_values=False,
                                                     scale_mass=False,
                                                     mass=cube_mass,
                                                     dynamic_friction=0.2,
                                                     static_friction=0.2,
                                                     bounciness=cube_bounciness))
            commands.extend([c.get_add_material(cube_visual_material, library="materials_low.json"),
                             {"$type": "set_visual_material",
                              "id": cube_id,
                              "material_name": cube_visual_material,
                              "object_name": "cube",
                              "material_index": 0}])
            # Define audio for the cube.
            cube_audio = ClatterObject(impact_material=cube_audio_material,
                                       amp=0.2,
                                       resonance=0.25,
                                       size=1)
            # Reset Clatter.
            clatter.reset(simulation_amp=0.9,
                          objects={cube_id: cube_audio},
                          scrape_angle=0,
                          impact_area_ratio=100,
                          roll_angular_speed=100,
                          max_contact_separation=1,
                          random_seed=0)
            c.communicate(commands)
            recorder.start(path=path.joinpath(f"{scrape_surface_model_name}_{cube_audio_material.name}_{force}.wav"))
            # Apply a lateral force to start scraping.
            c.communicate({"$type": "apply_force_magnitude_to_object",
                           "magnitude": force,
                           "id": cube_id})
            while not recorder.done:
                c.communicate([])
            # Destroy the objects to reset the scene.
            c.communicate([{"$type": "destroy_object",
                            "id": cube_id},
                           {"$type": "destroy_object",
                            "id": surface_id}])
c.communicate({"$type": "terminate"})
