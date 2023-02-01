from typing import List, Dict
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.impact_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION
from tdw.physics_audio.clatter_object import ClatterObject


class DemoReel(Controller):
    def start(self) -> None:
        self.communicate([{"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080}])

    def ball_and_plane(self, plane_visual_material: str, plane_impact_material: ImpactMaterial, plane_amp: float,
                       plane_resonance: float, object_visual_material: str, object_impact_material: ImpactMaterial,
                       object_amp: float, object_resonance: float, object_bounciness: float, object_y: float,
                       random_seed: int, object_scale: float = 0.1, object_mass: float = 0.05, object_size: int = 1,
                       object_name: str = "sphere", scene: str = "mm_craftroom_2b",
                       skybox: str = "kiara_8_sunset_4k") -> None:
        self.add_ons.clear()
        commands = [Controller.get_add_scene(scene),
                    Controller.get_add_material(plane_visual_material),
                    Controller.get_add_material(object_visual_material)]
        # Add the plane and set its visual material.
        plane_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=plane_id,
                                                          library="models_flex.json",
                                                          position={"x": 0, "y": 0.3, "z": 0},
                                                          kinematic=True,
                                                          scale_factor={"x": 1, "y": 0.05, "z": 1}))
        commands.append({"$type": "set_visual_material",
                         "material_name": plane_visual_material,
                         "object_name": "cube",
                         "id": plane_id})
        # Define the audio values for the plane.
        plane_audio: ClatterObject = ClatterObject(impact_material=plane_impact_material,
                                                   size=4,
                                                   amp=plane_amp,
                                                   resonance=plane_resonance,
                                                   fake_mass=100)
        # Add the object and set its visual material.
        object_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name=object_name,
                                                          object_id=object_id,
                                                          library="models_flex.json",
                                                          position={"x": 0, "y": object_y, "z": 0},
                                                          scale_factor={"x": object_scale, "y": object_scale, "z": object_scale},
                                                          default_physics_values=False,
                                                          dynamic_friction=DYNAMIC_FRICTION[object_impact_material],
                                                          static_friction=STATIC_FRICTION[object_impact_material],
                                                          bounciness=object_bounciness,
                                                          mass=object_mass))
        commands.append({"$type": "set_visual_material",
                         "material_name": object_visual_material,
                         "object_name": object_name,
                         "id": object_id})
        # Define the audio values for the object.
        object_audio: ClatterObject = ClatterObject(impact_material=object_impact_material,
                                                    size=object_size,
                                                    amp=object_amp,
                                                    resonance=object_resonance)
        lighting: InteriorSceneLighting = InteriorSceneLighting(hdri_skybox=skybox)
        camera: ThirdPersonCamera = ThirdPersonCamera(avatar_id="a",
                                                      position={"x": 0, "y": 0.9, "z": -1.4},
                                                      look_at={"x": 0, "y": 0.5, "z": 0})
        audio_initializer: AudioInitializer = AudioInitializer(avatar_id=camera.avatar_id)
        clatter: Clatter = Clatter(objects={plane_id: plane_audio,
                                            object_id: object_audio},
                                   simulation_amp=0.9,
                                   random_seed=random_seed)
        self.add_ons.extend([lighting, camera, audio_initializer, clatter])
        self.communicate(commands)
        for i in range(150):
            self.communicate([])

    def metal_sheet_ceramic_ball(self) -> None:
        self.ball_and_plane(plane_visual_material="metal_cast",
                            plane_impact_material=ImpactMaterial.wood_hard,
                            plane_amp=0.9,
                            plane_resonance=0.9,
                            object_visual_material="ceramic_raw_striped",
                            object_impact_material=ImpactMaterial.ceramic,
                            object_y=2,
                            object_amp=0.9,
                            object_bounciness=0.85,
                            object_resonance=0.05,
                            random_seed=2)

    def metal_sheet_big_ceramic_ball(self) -> None:
        self.ball_and_plane(plane_visual_material="metal_cast",
                            plane_impact_material=ImpactMaterial.wood_hard,
                            plane_amp=0.9,
                            plane_resonance=0.9,
                            object_visual_material="ceramic_raw_striped",
                            object_impact_material=ImpactMaterial.ceramic,
                            object_y=2,
                            object_amp=0.9,
                            object_bounciness=0.85,
                            object_resonance=0.05,
                            object_scale=0.2,
                            object_mass=0.2,
                            object_size=2,
                            random_seed=2)

    def wood_sheet_metal_ball(self) -> None:
        self.ball_and_plane(plane_visual_material="parquet_wood_oak_brown",
                            plane_impact_material=ImpactMaterial.wood_hard,
                            plane_amp=0.9,
                            plane_resonance=0.9,
                            object_visual_material="metal_sandblasted",
                            object_impact_material=ImpactMaterial.metal,
                            object_y=2,
                            object_amp=0.1,
                            object_bounciness=0.85,
                            object_resonance=0.05,
                            object_size=3,
                            random_seed=3)

    def wood_sheet_multiple_balls(self) -> None:
        plane_visual_material = "parquet_wood_oak_brown"
        plane_impact_material = ImpactMaterial.wood_hard
        plane_amp = 0.9
        plane_resonance = 0.9
        scene = "mm_craftroom_2b"
        skybox = "kiara_8_sunset_4k"
        object_name = "sphere"
        object_size = 1
        random_seed = 2
        object_scale = {"x": 0.1, "y": 0.1, "z": 0.1}
        object_visual_materials = ["ceramic_raw_striped",
                                   "metal_sandblasted",
                                   "plastic_vinyl_glossy",
                                   "plastic_vinyl_glossy_red"]
        object_impact_materials = [ImpactMaterial.ceramic,
                                   ImpactMaterial.metal,
                                   ImpactMaterial.plastic_hard,
                                   ImpactMaterial.plastic_hard]
        object_amps = [0.9, 0.1, 0.2, 0.2]
        object_masses = [0.05, 0.15, 0.2, 0.03]
        object_resonance = 0.05
        self.add_ons.clear()
        commands = [Controller.get_add_scene(scene),
                    Controller.get_add_material(plane_visual_material)]
        # Add the plane and set its visual material.
        plane_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=plane_id,
                                                          library="models_flex.json",
                                                          position={"x": 0, "y": 0.3, "z": 0},
                                                          kinematic=True,
                                                          scale_factor={"x": 1, "y": 0.05, "z": 1}))
        commands.append({"$type": "set_visual_material",
                         "material_name": plane_visual_material,
                         "object_name": "cube",
                         "id": plane_id})
        # Define the audio values for the plane.
        plane_audio: ClatterObject = ClatterObject(impact_material=plane_impact_material,
                                                   size=4,
                                                   amp=plane_amp,
                                                   resonance=plane_resonance,
                                                   fake_mass=100)
        # Add the objects and set their visual materials.
        x = -0.4
        y = 2
        clatter_objects = {plane_id: plane_audio}
        for visual_material, mass, impact_material, amp in zip(object_visual_materials,
                                                               object_masses,
                                                               object_impact_materials,
                                                               object_amps):
            commands.append(Controller.get_add_material(visual_material))
            object_id = Controller.get_unique_id()
            commands.extend(Controller.get_add_physics_object(model_name=object_name,
                                                              object_id=object_id,
                                                              library="models_flex.json",
                                                              position={"x": x, "y": y, "z": 0},
                                                              scale_factor=object_scale,
                                                              default_physics_values=False,
                                                              dynamic_friction=DYNAMIC_FRICTION[impact_material],
                                                              static_friction=STATIC_FRICTION[impact_material],
                                                              bounciness=0.85,
                                                              mass=mass))
            commands.append({"$type": "set_visual_material",
                             "material_name": visual_material,
                             "object_name": object_name,
                             "id": object_id})
            # Define the audio values for the object.
            object_audio: ClatterObject = ClatterObject(impact_material=impact_material,
                                                        size=object_size,
                                                        amp=amp,
                                                        resonance=object_resonance)
            x += 0.15
            y += 0.1
            clatter_objects[object_id] = object_audio
        lighting: InteriorSceneLighting = InteriorSceneLighting(hdri_skybox=skybox)
        camera: ThirdPersonCamera = ThirdPersonCamera(avatar_id="a",
                                                      position={"x": 0, "y": 0.9, "z": -1.4},
                                                      look_at={"x": 0, "y": 0.5, "z": 0})
        audio_initializer: AudioInitializer = AudioInitializer(avatar_id=camera.avatar_id)
        clatter: Clatter = Clatter(objects=clatter_objects,
                                   simulation_amp=0.9,
                                   random_seed=random_seed)
        self.add_ons.extend([lighting, camera, audio_initializer, clatter])
        self.communicate(commands)
        for i in range(150):
            self.communicate([])



if __name__ == "__main__":
    c = DemoReel()
    c.start()
    # c.metal_sheet_ceramic_ball()
    # c.metal_sheet_big_ceramic_ball()
    # c.wood_sheet_metal_ball()
    c.wood_sheet_multiple_balls()
    c.communicate({"$type": "terminate"})
