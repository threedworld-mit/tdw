from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.py_impact import PyImpact
from tdw.librarian import ModelLibrarian
from typing import List, Dict
from pathlib import Path
import json
from argparse import ArgumentParser

"""
Create a "Rube Goldberg machine" from a set of objects that will collide when the first is struck by a ball.
Impact sounds are generated for each collision.

Scene setup is handled through a json file -- object_setup.json -- which defines the id number, position, rotation and 
scale for every object in the scene. Each entry in the file is deserialized into an ObjectSetup object.

Note that all scene objects have also been added to the default audio and material data file
(Python/tdw/py_impact/objects.csv), and all required parameters entered including their masses, audio material used,
bounciness and relative amplitudes. See Documentation/misc_frontend/impact_sounds.md for additional details. 

This use-case also demonstrates the use of mode properties logging in PyImpact.
"""

class _ObjectSetup:
    """
    Metadata for scene object setup. Specifies the id, position, rotation and scale of object.
    """
    def __init__(self,
                 id: int,
                 model_name: str,
                 position: Dict[str, float] = TDWUtils.VECTOR3_ZERO,
                 rotation: Dict[str, float] = TDWUtils.VECTOR3_ZERO,
                 scale: Dict[str, float] = {"x": 1, "y": 1, "z": 1}):
        """
        :param id: ID number of object in scene. We assign, rather than generating unique ID (see below).
        :param model_name: Actual model name of the object (i.e. TDW model library name).
        :param position: The initial position of the object as a Vector3 dictionary.
        :param rotation: The initial rotation of the object in Euler angles as a Vector3 dictionary.
        :param scale: The initial scale of the object as a Vector3 dictionary.
        """

        self.id = id 
        self.model_name = model_name
        self.position = position
        self.rotation = rotation
        self.scale = scale


class RubeGoldbergDemo(Controller):

    def __init__(self):
        self.obj_name_dict: Dict[int, str] = {}
        
        # Set up the object transform data.
        object_setup_data = json.loads(Path("object_setup.json").read_text())
        self.object_setups: List[_ObjectSetup] = []
        for o in object_setup_data:
            combo = _ObjectSetup(id=int(o),
                                 model_name=object_setup_data[o]["model_name"],
                                 position=object_setup_data[o]["position"],
                                 rotation=object_setup_data[o]["rotation"],
                                 scale=object_setup_data[o]["scale"])
            self.object_setups.append(combo)

        # Parse the default objects.csv spreadsheet. 
        self.object_audio_data = PyImpact.get_object_info()

        self.temp_amp = 0.1

        # Keep track of the current trial number, for logging purposes.
        self.current_trial_num = 0

        # Fetch the ball and board model's records; we will need them later to change its material.
        self.special_models = ModelLibrarian(library="models_special.json")
        self.full_models = ModelLibrarian(library="models_full.json")
        self.ball_record = self.special_models.get_record("prim_sphere")
        self.board_record = self.full_models.get_record("wood_board")

        # Set path to write out logging info.
        self.root_dest_dir = Path("dist/mode_properties_logs")
        if not self.root_dest_dir.exists():
            self.root_dest_dir.mkdir(parents=True)

        super().__init__()
 
 
    def run(self, num_trials: int):
        """
        Build a "Rube Goldberg" machine to produce impact sounds.
        """

        # Load the photorealistic "archviz_house" environment.
        self.load_streamed_scene(scene="archviz_house")

        # Organize all initialization commands into a single list.
        # Set global values, including the desired screen size and aspect ratio (720P).
        # Frame rate is set to 60 fps to facilitate screen / video recording.
        init_commands = [{"$type": "set_render_quality",
                          "render_quality": 5},
                         {"$type": "set_screen_size",
                          "width": 1280,
                          "height": 720},
                         {"$type": "set_target_framerate",
                          "framerate": 60},
                         {"$type": "set_time_step",
                          "time_step": 0.02}]

        # Create the avatar. 
        init_commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps_Kinematic",
                                                    position={"x": -15.57, "y": 1.886, "z": -4.97}))

        # Aim the avatar camera to frame the desired view.
        init_commands.extend([{"$type": "rotate_sensor_container_by",
                               "axis": "yaw",
                               "angle": 109.13,
                               "sensor_name": "SensorContainer",
                               "avatar_id": "a"},
                              {"$type": "rotate_sensor_container_by",
                               "axis": "pitch",
                               "angle": 6.36,
                               "sensor_name": "SensorContainer",
                               "avatar_id": "a"}])

        # Add the audio sensor.
        init_commands.extend([{"$type": "add_audio_sensor",
                               "avatar_id": "a"}])

        # Adjust post-processing settings.
        init_commands.extend([{"$type": "set_post_exposure",
                               "post_exposure": 0.35},
                             {"$type": "set_screen_space_reflections",
                              "enabled": True},
                             {"$type": "set_vignette",
                              "enabled": False},
                             {"$type": "set_ambient_occlusion_intensity",
                              "intensity": 0.175},
                             {"$type": "set_ambient_occlusion_thickness_modifier",
                              "thickness": 5.0}])

        # Set the shadow strength to maximum.
        init_commands.extend([{"$type": "set_shadow_strength",
                               "strength": 1.0}])

        # Send all of the initialization commands.
        self.communicate(init_commands)

        for i in range(num_trials):
            self.do_trial()
            

    def do_trial(self):
        # Initialize PyImpact and pass in the "master gain" amplitude value. This value must be betweem 0 and 1.
        # The relative amplitudes of all scene objects involved in collisions will be scaled relative to this value.
        # Note -- if this value is too high, waveform clipping can occur and the resultant audio will be distorted.
        # For this reason, the value used here is considerably smaller than the corresponding value used in the
        # impact_sounds.py example controller. Here we have a large number of closely-occuring collisions resulting in
        # a rapid series of "clustered" impact sounds, as opposed to a single object falling from a height;
        # using a higher value such as the 0.5 used in the example controller will definitely result in unpleasant
        # distortion of the audio.
        # Note that logging is also enabled.

        # Keep track of trial number.
        self.current_trial_num += 1

        # Create folder for this trial's logging info.
        dest_dir = self.root_dest_dir.joinpath(str(self.current_trial_num))
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True)
        dest_dir_str = str(dest_dir.resolve())

        p = PyImpact(0.25, logging=True)

        self.add_all_objects()

        # "Aim" the ball at the monkey and apply the force.
        # Note that this force value was arrived at through a number of trial-and-error iterations.
        resp = self.communicate([{"$type": "object_look_at_position",
                                  "id": 0,
                                  "position": {"x": -12.95, "y": 1.591, "z": -5.1}},
                                 {"$type": "apply_force_magnitude_to_object",
                                  "id": 0,
                                  "magnitude": 98.0}])

        for i in range(400):
            collisions, environment_collision, rigidbodies = PyImpact.get_collisions(resp)
            # Sort the objects by mass.
            masses: Dict[int, float] = {}
            for j in range(rigidbodies.get_num()):
                masses.update({rigidbodies.get_id(j): rigidbodies.get_mass(j)})

            # If there was a collision, create an impact sound.
            if len(collisions) > 0 and PyImpact.is_valid_collision(collisions[0]):
                collider_id = collisions[0].get_collider_id()
                collidee_id = collisions[0].get_collidee_id()
                # The "target" object should have less mass than the "other" object.
                if masses[collider_id] < masses[collidee_id]:
                    target_id = collider_id
                    other_id = collidee_id
                else:
                    target_id = collidee_id
                    other_id = collider_id

                target_name = self.obj_name_dict[target_id]
                other_name = self.obj_name_dict[other_id]

                impact_sound_command = p.get_impact_sound_command(
                    collision=collisions[0],
                    rigidbodies=rigidbodies,
                    target_id=target_id,
                    target_mat=self.object_audio_data[target_name].material,
                    other_id=other_id,
                    other_mat=self.object_audio_data[other_name].material,
                    target_amp=self.object_audio_data[target_name].amp,
                    other_amp=self.object_audio_data[other_name].amp,
                    resonance=self.object_audio_data[target_name].resonance)
                resp = self.communicate(impact_sound_command)
            # Continue to run the trial.
            else:
                resp = self.communicate([])

        # Get the logging info for this trial and write it out.
        log = p.get_log()
        json_dest = dest_dir.joinpath("mode_properties_log.json")
        json_dest.write_text(json.dumps(log, indent=2))

        for obj_setup in self.object_setups:
            self.communicate({"$type": "destroy_object", "id": obj_setup.id})

		

    def add_all_objects(self):
        object_commands = []
        rigidbodies = []

        # Set the mass and scale of the objects, from  the data files we parsed earlier.
        # Enable output of collision and rigid body data.
        # Build dictionary of id,,name so we can retrieve object names during collisions.
        # Cache the ids for objects we need to change materials for later
        for obj_setup in self.object_setups:
            self.obj_name_dict[obj_setup.id] = obj_setup.model_name
            rigidbodies.append(obj_setup.id)
            if obj_setup.model_name == "prim_sphere":
                ball_id = obj_setup.id
            elif obj_setup.model_name == "102_pepsi_can_12_fl_oz_vray":
                coke_can_id = obj_setup.id
            elif obj_setup.model_name == "wood_board":
                board_id = obj_setup.id
            elif obj_setup.model_name == "bench":
                table_id = obj_setup.id
            elif obj_setup.model_name == "camera_box":
                camera_box_id = obj_setup.id

            # Set up to add all objects
            object_commands.extend([self.get_add_object(
                                    model_name=obj_setup.model_name, 
                                    object_id=obj_setup.id,
                                    position=obj_setup.position,
                                    rotation=obj_setup.rotation,
                                    library=self.object_audio_data[obj_setup.model_name].library),
                                    {"$type": "set_mass",
                                    "id": obj_setup.id,
                                    "mass": self.object_audio_data[obj_setup.model_name].mass},
                                    {"$type": "set_object_collision_detection_mode", 
                                    "id": obj_setup.id, 
                                    "mode": "continuous_speculative"},
                                    {"$type": "scale_object", 
                                     "id":  obj_setup.id, 
                                     "scale_factor": obj_setup.scale}])

        object_commands.extend([{"$type": "send_collisions",
                                 "enter": True,
                                 "stay": False,
                                 "exit": False},
                                {"$type": "send_rigidbodies",
                                 "frequency": "always",
                                 "ids": rigidbodies}])

        # Scale the ball and set a suitable drag value to "tune" how hard it will hit the monkey.
        # This combined with the force applied below hits the monkey just hard enough to set the sequnce of
        # collisions in motion.
        object_commands.extend([{"$type": "scale_object",
                                 "id": ball_id,
                                 "scale_factor": {"x": 0.1, "y": 0.1, "z": 0.1}},
                                {"$type": "set_object_drag",
                                 "angular_drag": 5.0,
                                 "drag": 1.0,
                                 "id": ball_id}])

        # Set physics material parameters to enable rolling motion for the coke can and board after being hit,
        # so they collide with the row of "dominos"
        object_commands.extend([{"$type": "set_physic_material",
                                 "dynamic_friction": 0.4,
                                 "static_friction": 0.4,
                                 "bounciness": 0.6,
                                 "id": table_id},
                                {"$type": "set_physic_material",
                                 "dynamic_friction": 0.2,
                                 "static_friction": 0.2,
                                 "bounciness": 0.6,
                                 "id": coke_can_id},
                                {"$type": "set_physic_material",
                                 "dynamic_friction": 0.2,
                                 "static_friction": 0.2,
                                 "bounciness": 0.7,
                                 "id": board_id}])

        # Set the camera box and table to be kinematic, we don't need them to respond to physics.
        object_commands.extend([{"$type": "set_kinematic_state",
                                 "id": table_id,
                                 "is_kinematic": True},
                                {"$type": "set_kinematic_state",
                                 "id": camera_box_id,
                                 "is_kinematic": True}])

        # Set the visual material of the ball to metal and the board to a different wood than the bench.
        object_commands.extend(TDWUtils.set_visual_material(self, self.ball_record.substructure, ball_id,
                                                            "dmd_metallic_fine", quality="high"))
        object_commands.extend(TDWUtils.set_visual_material(self, self.board_record.substructure, board_id,
                                                            "wood_tropical_hardwood", quality="high"))

        # Send all of the object setup commands.
        self.communicate(object_commands)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--num", type=int, default=5, help="Number of trials.")
    args = parser.parse_args()

    RubeGoldbergDemo().run(args.num)
