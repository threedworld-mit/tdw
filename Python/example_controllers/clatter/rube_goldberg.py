from typing import List, Dict
from pathlib import Path
import json
from argparse import ArgumentParser
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw.add_ons.clatter import Clatter
from tdw.add_ons.audio_initializer import AudioInitializer
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.physics_audio_recorder import PhysicsAudioRecorder
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.physics_audio.clatter_object import ClatterObject
from tdw.physics_audio.impact_material import ImpactMaterial


class RubeGoldbergDemo(Controller):
    """
    Create a "Rube Goldberg machine" from a set of objects that will collide when the first is struck by a ball.

    Impact sounds are generated for each collision.

    Scene setup is handled through a json file -- rube_goldberg_object.json -- which defines the id number, position,
    rotation and scale for every object in the scene. For some objects, it also has non-default physics values.
    All other objects use default physics/audio values.

    This controller will output a .wav file of the trial.
    """

    BALL_ID: int = 0
    BOARD_ID: int = 2

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Cached commands to add the objects.
        self.init_object_commands: List[dict] = list()
        # Cached commands to destroy the objects.
        self.destroy_object_commands: List[dict] = list()
        # Cached audio override data.
        self.clatter_objects: Dict[int, ClatterObject] = dict()
        # Get commands to initialize the objects.
        object_setup_data = json.loads(Path("rube_goldberg_objects.json").read_text())
        for o in object_setup_data:
            object_id = int(o)
            if object_setup_data[o]["library"] not in Controller.MODEL_LIBRARIANS:
                Controller.MODEL_LIBRARIANS[object_setup_data[o]["library"]] = ModelLibrarian(object_setup_data[o]["library"])
            clatter_values = Controller.MODEL_LIBRARIANS[object_setup_data[o]["library"]].get_record(object_setup_data[o]["model_name"]).clatter_values
            # Cache the command to destroy the object.
            self.destroy_object_commands.append({"$type": "destroy_object",
                                                 "id": object_id})
            # Use non-default physics values.
            if "physics" in object_setup_data[o]:
                self.init_object_commands.extend(self.get_add_physics_object(model_name=object_setup_data[o]["model_name"],
                                                                             object_id=object_id,
                                                                             position=object_setup_data[o]["position"],
                                                                             rotation=object_setup_data[o]["rotation"],
                                                                             scale_factor=object_setup_data[o]["scale"],
                                                                             library=object_setup_data[o]["library"],
                                                                             default_physics_values=False,
                                                                             scale_mass=False,
                                                                             kinematic=object_setup_data[o]["physics"]["kinematic"],
                                                                             mass=object_setup_data[o]["physics"]["mass"],
                                                                             dynamic_friction=object_setup_data[o]["physics"]["dynamic_friction"],
                                                                             static_friction=object_setup_data[o]["physics"]["static_friction"],
                                                                             bounciness=object_setup_data[o]["physics"]["bounciness"]))
                # Use audio values from the JSON data.
                if "audio" in object_setup_data[o]:
                    a = object_setup_data[o]["audio"]
                    clatter_object: ClatterObject = ClatterObject(impact_material=ImpactMaterial[a["impact_material"]],
                                                                  size=a["size"],
                                                                  amp=a["amp"],
                                                                  resonance=a["resonance"],
                                                                  fake_mass=a["fake_mass"])
                # Use default audio values but adjust the mass.
                else:
                    clatter_object: ClatterObject = ClatterObject(impact_material=clatter_values.impact_material,
                                                                  amp=clatter_values.amp,
                                                                  resonance=clatter_values.resonance,
                                                                  size=clatter_values.size,
                                                                  fake_mass=object_setup_data[o]["physics"]["mass"])
                self.clatter_objects[object_id] = clatter_object
            # Use default physics values.
            else:
                self.init_object_commands.extend(self.get_add_physics_object(model_name=object_setup_data[o]["model_name"],
                                                                             object_id=object_id,
                                                                             position=object_setup_data[o]["position"],
                                                                             rotation=object_setup_data[o]["rotation"],
                                                                             scale_factor=object_setup_data[o]["scale"],
                                                                             scale_mass=False,
                                                                             library=object_setup_data[o]["library"]))
                # Use default audio values but lower the resonance.
                clatter_object: ClatterObject = ClatterObject(impact_material=clatter_values.impact_material,
                                                              amp=clatter_values.amp,
                                                              resonance=0.05,
                                                              size=clatter_values.size)
                self.clatter_objects[object_id] = clatter_object
            # Set the collision detection mode.
            self.init_object_commands.append({"$type": "set_object_collision_detection_mode",
                                              "id": object_id,
                                              "mode": "continuous_speculative"})
        # "Aim" the ball at the monkey and apply the force.
        # Note that this force value was arrived at through a number of trial-and-error iterations.
        # Set a suitable drag value to "tune" how hard it will hit the monkey.
        self.init_object_commands.extend([{"$type": "object_look_at_position",
                                           "id": RubeGoldbergDemo.BALL_ID,
                                           "position": {"x": -12.95, "y": 1.8, "z": -5.1}},
                                          {"$type": "apply_force_magnitude_to_object",
                                           "id": RubeGoldbergDemo.BALL_ID,
                                           "magnitude": 20},
                                          {"$type": "set_object_drag",
                                           "angular_drag": 5.0,
                                           "drag": 1.0,
                                           "id": RubeGoldbergDemo.BALL_ID}])
        # Set the visual material of the ball to metal and the board to a different wood than the bench.
        self.init_object_commands.extend(TDWUtils.set_visual_material(self,
                                                                      ModelLibrarian("models_special.json").get_record("prim_sphere").substructure,
                                                                      RubeGoldbergDemo.BALL_ID,
                                                                      "dmd_metallic_fine",
                                                                      quality="high"))
        self.init_object_commands.extend(TDWUtils.set_visual_material(self,
                                                                      ModelLibrarian("models_core.json").get_record("wood_board").substructure,
                                                                      RubeGoldbergDemo.BOARD_ID,
                                                                      "wood_tropical_hardwood",
                                                                      quality="high"))
        # Add a camera.
        camera = ThirdPersonCamera(position={"x": -15.57, "y": 1.886, "z": -4.97},
                                   avatar_id="a",
                                   rotation={"x": 6.36, "y": 109.13, "z": 0})
        # Initialize audio.
        audio_initializer = AudioInitializer(avatar_id="a")

        # Set the floor object.
        env = ClatterObject(impact_material=ImpactMaterial.wood_medium, size=5,
                            amp=0.1, resonance=0.01, fake_mass=500)

        # Add Clatter.
        # Here we have a large number of closely-occurring collisions resulting in a rapid series of "clustered" impact sounds, as opposed to a single object falling from a height.
        # Using a higher value such as the 0.5 used in the example controller will definitely result in unpleasant distortion of the audio.
        # Set `roll_substitute` to `"none"` to prevent spurious roll audio sounds.
        # The other parameters set here will reduce the number of audio events overall and set the environment (floor).
        self.clatter: Clatter = Clatter(objects=self.clatter_objects, simulation_amp=0.2, roll_substitute="none",
                                        roll_angular_speed=15, min_collision_speed=0.01, max_num_events=25,
                                        max_num_contacts=4, environment=env)
        # Add a recorder.
        self.recorder: PhysicsAudioRecorder = PhysicsAudioRecorder(max_frames=200)
        # Add the add-ons.
        self.add_ons.extend([camera, audio_initializer, self.clatter, self.recorder])

        # Keep track of the current trial number, for logging purposes.
        self.current_trial_num = 0

        # Set path to write out logging info.
        self.output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("rube_goldberg")
        print(f".wav files will be output to: {self.output_directory}")
        if not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)

    def run(self, num_trials: int) -> None:
        """
        Build a "Rube Goldberg" machine to produce impact sounds.
        """

        # Load the photorealistic "archviz_house" environment.
        # Set global values, including the desired screen size and aspect ratio (720P).
        # Adjust post-processing settings.
        # Set the shadow strength to maximum.
        self.communicate([self.get_add_scene(scene_name="archviz_house"),
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_screen_size",
                           "width": 1280,
                           "height": 720},
                          {"$type": "set_time_step",
                           "time_step": 0.02},
                          {"$type": "set_post_exposure",
                           "post_exposure": 0.35},
                          {"$type": "set_screen_space_reflections",
                           "enabled": True},
                          {"$type": "set_vignette",
                           "enabled": False},
                          {"$type": "set_ambient_occlusion_intensity",
                           "intensity": 0.175},
                          {"$type": "set_ambient_occlusion_thickness_modifier",
                           "thickness": 5.0},
                          {"$type": "set_shadow_strength",
                           "strength": 1.0}])
        for i in range(num_trials):
            self.do_trial()
        self.communicate({"$type": "terminate"})

    def do_trial(self):
        # Keep track of trial number.
        self.current_trial_num += 1
        # Create folder for this trial's images.
        dest_dir = self.output_directory.joinpath(str(self.current_trial_num))
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        # Reset Clatter.
        self.clatter.reset(objects=self.clatter_objects)
        # Initialize the objects.
        self.communicate(self.init_object_commands)
        # Start recording audio.
        self.recorder.start(path=dest_dir.joinpath("audio.wav"))
        # Record audio.
        while not self.recorder.done:
            self.communicate([])
        # Destroy the objects.
        self.communicate(self.destroy_object_commands)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--num", type=int, default=5, help="Number of trials.")
    parser.add_argument("--launch_build", action="store_true", help="Auto-launch the build")
    args = parser.parse_args()

    RubeGoldbergDemo(launch_build=args.launch_build).run(args.num)
