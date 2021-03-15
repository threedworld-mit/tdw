import random
import os
import shutil
from time import sleep
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.py_impact import PyImpact
from tdw.output_data import OutputData, Images
from PIL import Image, ImageFont, ImageDraw  

"""
- Listen for collisions between objects.
- Generate an impact sound with py_impact upon impact and play the sound in the build.
"""


class ImpactSounds(Controller):
    def trial(self, test_material_name):
        """
        Select random objects and collide them to produce impact sounds.
        """

        p = PyImpact(initial_amp=0.5)

        print("Testing material " + test_material_name)

        # Destroy all objects currently in the scene.
        # Set the screen size.
        # Adjust physics timestep for more real-time physics behavior.
        commands = [{"$type": "destroy_all_objects"},
                    {"$type": "set_screen_size",
                     "width": 1024,
                     "height": 1024},
                    {"$type": "set_time_step",
                     "time_step": 0.02}]
        # Create the avatar.
        commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps_Kinematic",
                                               position={"x": 1, "y": 1.2, "z": 1.2},
                                               look_at=TDWUtils.VECTOR3_ZERO))

        # Add the audio sensor.
        # Set the target framerate.
        # Make sure that post-processing is enabled and render quality is set to max.
        commands.extend([{"$type": "add_audio_sensor",
                          "avatar_id": "a"},
                         {"$type": "set_target_framerate",
                          "framerate": 60},
                         {"$type": "set_post_process",
                          "value": True},
                         {"$type": "set_focus_distance",
                          "focus_distance": 2},
                         {"$type": "set_render_quality",
                          "render_quality": 5}])

        # Select a random pair of objects.
        objects = PyImpact.get_object_info()
        obj1_names = ["marble_table"]
        obj2_names = ["iron_box"]
        obj1_name = random.choice(obj1_names)
        obj2_name = random.choice(obj2_names)
        obj1_id = 0
        obj2_id = 1

        # Add the objects.
        # Set their masses from the audio info data.
        # Set a physics material for the second object.
        # Apply a force to the second object.
        # Listen for collisions, and object properties.
        commands.extend([self.get_add_object(model_name=obj1_name, object_id=obj1_id,
                                             library=objects[obj1_name].library),
                         {"$type": "set_mass",
                          "id": obj1_id,
                          "mass": objects[obj1_name].mass},
                         self.get_add_object(model_name=obj2_name, object_id=obj2_id,
                                             library=objects[obj2_name].library,
                                             rotation={"x": 135, "y": 0, "z": 30},
                                             position={"x": 0, "y": 2, "z": 0}),
                         {"$type": "set_mass",
                          "id": obj2_id,
                          "mass": objects[obj2_name].mass},
                         {"$type": "set_physic_material",
                          "id": obj2_id,
                          "bounciness": objects[obj2_name].bounciness,
                          "dynamic_friction": 0.8},
                         {"$type": "apply_force_to_object",
                          "force": {"x": 0, "y": -0.01, "z": 0},
                          "id": obj2_id},
                         {"$type": "send_collisions",
                          "enter": True,
                          "stay": False,
                          "exit": False},
                         {"$type": "send_rigidbodies",
                          "frequency": "always",
                          "ids": [obj2_id, obj1_id]}])

        # Send all of the commands.
        resp = self.communicate(commands)

        # Iterate through 200 frames.
        # Every frame, listen for collisions, and parse the output data.
        for i in range(200):
            collisions, environment_collision, rigidbodies = PyImpact.get_collisions(resp)
            # If there was a collision, create an impact sound.
            if len(collisions) > 0 and PyImpact.is_valid_collision(collisions[0]):
                impact_sound_command = p.get_impact_sound_command(
                    collision=collisions[0],
                    rigidbodies=rigidbodies,
                    target_id=obj2_id,
                    target_mat=test_material_name,
                    target_amp=objects[obj2_name].amp,
                    other_id=obj1_id,
                    other_amp=objects[obj1_name].amp,
                    other_mat=objects[obj1_name].material.name + "_" + str(objects[obj1_name].size),
                    resonance=objects[obj2_name].resonance)
                resp = self.communicate(impact_sound_command)
            # Continue to run the trial.
            else:
                resp = self.communicate([])

        # Stop listening for collisions and rigidbodies.
        self.communicate([{"$type": "send_collisions",
                          "frequency": "never"},
                         {"$type": "send_rigidbodies",
                          "frequency": "never"}])

    def run(self):
        self.start()

        # Create the room.
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Run a series of trials.
        material_list = ["ceramic", "wood_hard", "wood_medium", "wood_soft", "metal", "glass", "paper", "cardboard", "leather", "fabric", "plastic_hard", "plastic_soft_foam", "rubber", "stone"]
        for mat in material_list:
            # Just do 0-4 for now, for testing
            for i in range(5):
                mat_n = mat + "_" + str(i)
                self.trial(mat_n)

        # Terminate the build.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    ImpactSounds(launch_build=False).run()

