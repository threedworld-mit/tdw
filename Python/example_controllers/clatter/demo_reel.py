from os import chdir
from time import sleep
from io import BytesIO
from typing import Dict
import re
from subprocess import run, PIPE, DEVNULL
from pathlib import Path
from shutil import rmtree
from PIL import Image
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.ui import UI
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.interior_scene_lighting import InteriorSceneLighting
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.impact_material_constants import DYNAMIC_FRICTION, STATIC_FRICTION
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.librarian import ModelLibrarian
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class DemoReel(Controller):
    Controller.MODEL_LIBRARIANS["models_flex.json"] = ModelLibrarian("models_flex.json")
    Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate([{"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080}])
        self.audio_device: str = self.get_audio_device()
        self.window_position: Dict[str, float] = TDWUtils.get_expected_window_position(window_width=1920,
                                                                                       window_height=1080,
                                                                                       monitor_index=1,
                                                                                       title_bar_height=12)
        self.output_directory: Path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("clatter_demo_reel").resolve()
        if self.output_directory.exists():
            rmtree(str(self.output_directory))
        self.output_directory.mkdir(parents=True)
        self.filename: int = 0

    def intro_splash(self) -> None:
        self.add_ons.clear()
        ui = UI()
        self.add_ons.append(ui)
        self.communicate([])
        # Add an empty black image. Source: https://stackoverflow.com/a/38626806
        with BytesIO() as output:
            Image.new(mode="RGB", size=(16, 16)).save(output, "PNG")
            image = output.getvalue()
        ui.add_image(image,
                     position={"x": 0, "y": 0},
                     size={"x": 16, "y": 16},
                     rgba=False,
                     scale_factor={"x": 2000, "y": 2000})
        ui.add_text(text="Clatter",
                    font_size=64,
                    position={"x": 0, "y": 0})
        ui.add_text(text="Physically-driven audio synthesis",
                    font_size=32,
                    position={"x": 0, "y": -64},
                    pivot={"x": 0.5, "y": 1})
        ui.add_text(text="https://alters-mit.github.io/clatter/",
                    font_size=32,
                    position={"x": 0, "y": -130},
                    pivot={"x": 0.5, "y": 1})
        self.communicate([])
        self.start_video_capture()
        sleep(5)
        ui.destroy_all(destroy_canvas=True)
        self.communicate({"$type": "stop_video_capture"})

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
                                                          scale_mass=False,
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
                                   random_seed=random_seed,
                                   roll_substitute="none")
        self.add_ons.extend([lighting, camera, audio_initializer, clatter])
        self.communicate(commands)
        self.play(150)

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
                                                              scale_mass=False,
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
                                   random_seed=random_seed,
                                   roll_substitute="none")
        self.add_ons.extend([lighting, camera, audio_initializer, clatter])
        self.communicate(commands)
        self.play(150)

    def scrape(self, object_visual_material: str, object_impact_material: ImpactMaterial, random_seed: int, force: float,
               scene: str = "mm_kitchen_4b", skybox: str = "sunset_fairway_4k", table_name: str = "quatre_dining_table",
               object_name: str = "cube", object_bounciness: float = 0.4, object_scale: float = 0.1,
               object_mass: float = 1, object_amp: float = 0.2, object_resonance: float = 0.25,
               object_dynamic_friction: float = 0.2, object_static_friction: float = 0.2, object_size: int = 1,
               object_y_offset: float = 0, frames: int = 100) -> None:
        self.add_ons.clear()
        commands = [Controller.get_add_scene(scene),
                    Controller.get_add_material(object_visual_material)]
        # Add the table and set its visual material.
        table_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name=table_name,
                                                          object_id=table_id,
                                                          library="models_core.json",
                                                          kinematic=True))
        # Add the object and set its visual material.
        object_id = Controller.get_unique_id()
        surface_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_name)
        commands.extend(Controller.get_add_physics_object(model_name=object_name,
                                                          object_id=object_id,
                                                          library="models_flex.json",
                                                          position={"x": 0,
                                                                    "y":  surface_record.bounds["top"]["y"] + object_y_offset,
                                                                    "z": surface_record.bounds["back"]["z"] + 0.1},
                                                          scale_factor={"x": object_scale,
                                                                        "y": object_scale,
                                                                        "z": object_scale},
                                                          default_physics_values=False,
                                                          scale_mass=False,
                                                          dynamic_friction=object_dynamic_friction,
                                                          static_friction=object_static_friction,
                                                          bounciness=object_bounciness,
                                                          mass=object_mass))
        commands.append({"$type": "set_visual_material",
                         "material_name": object_visual_material,
                         "object_name": object_name,
                         "id": object_id})
        # Apply a force.
        commands.append({"$type": "apply_force_magnitude_to_object",
                         "magnitude": force,
                         "id": object_id})
        # Define the audio values for the object.
        object_audio: ClatterObject = ClatterObject(impact_material=object_impact_material,
                                                    size=object_size,
                                                    amp=object_amp,
                                                    resonance=object_resonance)
        lighting: InteriorSceneLighting = InteriorSceneLighting(hdri_skybox=skybox)
        camera: ThirdPersonCamera = ThirdPersonCamera(avatar_id="a",
                                                      position={"x": 1.3, "y": 2, "z": -1.5},
                                                      look_at={"x": 0, "y": 0.8, "z": 0})
        audio_initializer: AudioInitializer = AudioInitializer(avatar_id=camera.avatar_id)
        clatter: Clatter = Clatter(objects={object_id: object_audio},
                                   simulation_amp=0.9,
                                   random_seed=random_seed)
        self.add_ons.extend([lighting, camera, audio_initializer, clatter])
        self.communicate(commands)
        self.communicate([])
        self.play(frames, delay=1)

    def scrape_wood(self) -> None:
        self.scrape(object_visual_material="wood_beech_natural",
                    object_impact_material=ImpactMaterial.wood_medium,
                    random_seed=0,
                    force=3)

    def crash(self, object_visual_material: str = "wood_beech_natural",
              object_impact_material: ImpactMaterial = ImpactMaterial.wood_medium,
              random_seed: int = 0, force: float = 3.5,
              scene: str = "mm_kitchen_4b", skybox: str = "sunset_fairway_4k", table_name: str = "quatre_dining_table",
              object_name: str = "cube", object_bounciness: float = 0.5, object_scale: float = 0.1,
              object_mass: float = 1, object_amp: float = 0.2, object_resonance: float = 0.25,
              object_dynamic_friction: float = 0.2, object_static_friction: float = 0.2, object_size: int = 1,
              frames: int = 100) -> None:
        self.add_ons.clear()
        commands = [Controller.get_add_scene(scene),
                    Controller.get_add_material(object_visual_material)]
        # Add the table and set its visual material.
        table_id = Controller.get_unique_id()
        commands.extend(Controller.get_add_physics_object(model_name=table_name,
                                                          object_id=table_id,
                                                          library="models_core.json",
                                                          kinematic=True))
        objects: Dict[int, ClatterObject] = dict()
        # Add the objects and set their visual materials.
        for d in [1, -1]:
            object_id = Controller.get_unique_id()
            surface_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_name)
            y = surface_record.bounds["top"]["y"]
            commands.extend(Controller.get_add_physics_object(model_name=object_name,
                                                              object_id=object_id,
                                                              library="models_flex.json",
                                                              position={"x": 0,
                                                                        "y": y,
                                                                        "z": (surface_record.bounds["back"]["z"] + 0.2) * d},
                                                              scale_factor={"x": object_scale,
                                                                            "y": object_scale,
                                                                            "z": object_scale},
                                                              default_physics_values=False,
                                                              scale_mass=False,
                                                              dynamic_friction=object_dynamic_friction,
                                                              static_friction=object_static_friction,
                                                              bounciness=object_bounciness,
                                                              mass=object_mass))
            commands.append({"$type": "set_visual_material",
                             "material_name": object_visual_material,
                             "object_name": object_name,
                             "id": object_id})
            # Apply a force.
            commands.append({"$type": "apply_force_magnitude_to_object",
                             "magnitude": force * d,
                             "id": object_id})
            objects[object_id] = ClatterObject(impact_material=object_impact_material,
                                               size=object_size,
                                               amp=object_amp,
                                               resonance=object_resonance)
        lighting: InteriorSceneLighting = InteriorSceneLighting(hdri_skybox=skybox)
        camera: ThirdPersonCamera = ThirdPersonCamera(avatar_id="a",
                                                      position={"x": 1.3, "y": 2, "z": -1.5},
                                                      look_at={"x": 0, "y": 0.8, "z": 0})
        audio_initializer: AudioInitializer = AudioInitializer(avatar_id=camera.avatar_id)
        clatter: Clatter = Clatter(objects=objects,
                                   simulation_amp=0.9,
                                   random_seed=random_seed)
        self.add_ons.extend([lighting, camera, audio_initializer, clatter])
        self.communicate(commands)
        self.play(frames, delay=1)

    @staticmethod
    def get_audio_device() -> str:
        resp = run(["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
                   stdout=DEVNULL,
                   stderr=PIPE).stderr.decode()
        return re.search(r'(Stereo Mix(.*))"', resp).group(1)

    def start_video_capture(self) -> None:
        self.communicate({"$type": "start_video_capture_windows",
                          "output_path": str(self.output_directory.joinpath(f"{self.filename}.mp4")),
                          "position": self.window_position,
                          "audio_device": self.audio_device,
                          "qp": 0})
        self.filename += 1

    def play(self, frames: int, delay: float = 0) -> None:
        self.start_video_capture()
        if delay > 0:
            sleep(delay)
        for i in range(frames):
            self.communicate([])
        self.communicate({"$type": "stop_video_capture"})

    def concat(self) -> None:
        text = ""
        chdir(str(self.output_directory))
        for f in self.output_directory.iterdir():
            fixed_filename = f"{f.stem}_fixed.mp4"
            text += f"file '{fixed_filename}'\n"
            run(["ffmpeg", "-y", "-itsoffset", "00:00:00.2", "-i", f.name, fixed_filename],
                stderr=DEVNULL)
        self.output_directory.joinpath("videos.txt").write_text(text.strip())
        run(["ffmpeg", "-f", "concat", "-i", "videos.txt", "-c", "copy", "demo_reel.mp4"],
            stderr=DEVNULL)


if __name__ == "__main__":
    c = DemoReel()
    c.intro_splash()
    c.metal_sheet_ceramic_ball()
    c.metal_sheet_big_ceramic_ball()
    c.wood_sheet_metal_ball()
    c.wood_sheet_multiple_balls()
    c.scrape_wood()
    c.crash()
    c.intro_splash()
    c.concat()
    c.communicate({"$type": "terminate"})
