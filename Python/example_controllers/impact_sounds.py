import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.py_impact import PyImpact, AudioMaterial
from tdw.object_init_data import AudioInitData

"""
- Listen for collisions between objects.
- Generate an impact sound with py_impact upon impact and play the sound in the build.
"""


class ImpactSounds(Controller):
    def trial(self):
        """
        Select random objects and collide them to produce impact sounds.
        """

        p = PyImpact(initial_amp=0.5)
        # Set the environment audio materials.
        floor = AudioMaterial.ceramic
        wall = AudioMaterial.wood_soft

        # Create an empty room.
        # Set the screen size.
        # Adjust framerate so that physics is closer to realtime.
        commands = [TDWUtils.create_empty_room(12, 12),
                    {"$type": "destroy_all_objects"},
                    {"$type": "set_screen_size",
                     "width": 1024,
                     "height": 1024},
                    {"$type": "set_target_framerate",
                     "framerate": 100}]
        # Create the avatar.
        commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps_Kinematic",
                                               position={"x": 1, "y": 1.2, "z": 1.2},
                                               look_at=TDWUtils.VECTOR3_ZERO))
        # Add the audio sensor.
        commands.extend([{"$type": "add_audio_sensor",
                          "avatar_id": "a"},
                         {"$type": "set_focus_distance",
                          "focus_distance": 2}])

        # Select a random pair of objects.
        obj1_names = ["trapezoidal_table", "glass_table_round", "yellow_side_chair", "table_square", "marble_table"]
        obj2_names = ["vase_06", "spoon1", "glass3", "jug02"]
        obj1_name = random.choice(obj1_names)
        obj2_name = random.choice(obj2_names)

        # Get initialization data from the default audio data (which includes mass, friction values, etc.).
        obj1_init_data = AudioInitData(name=obj1_name)
        obj2_init_data = AudioInitData(name=obj2_name,
                                       position={"x": 0, "y": 2, "z": 0},
                                       rotation={"x": 135, "y": 0, "z": 30})
        # Convert the initialization data to commands.
        obj1_id, obj1_commands = obj1_init_data.get_commands()
        obj2_id, obj2_commands = obj2_init_data.get_commands()

        # Cache the IDs and names of each object for PyImpact.
        object_names = {obj1_id: obj1_name,
                        obj2_id: obj2_name}
        p.set_default_audio_info(object_names=object_names)

        # Add the objects.
        commands.extend(obj1_commands)
        commands.extend(obj2_commands)
        # Apply a small force to the dropped object.
        # Request collision and rigidbody output data.
        commands.extend([{"$type": "apply_force_to_object",
                          "force": {"x": 0, "y": -0.01, "z": 0},
                          "id": obj2_id},
                         {"$type": "send_collisions",
                          "enter": True,
                          "stay": False,
                          "exit": False,
                          "collision_types": ["obj", "env"]},
                         {"$type": "send_rigidbodies",
                          "frequency": "always",
                          "ids": [obj2_id, obj1_id]}])
        # Send all of the commands.
        resp = self.communicate(commands)

        # Iterate through 200 frames.
        # Every frame, listen for collisions, and parse the output data.
        for i in range(200):
            # Use PyImpact to generate audio from the output data and then convert the audio to TDW commands.
            # If no audio is generated, then `commands` is an empty list.
            commands = p.get_audio_commands(resp=resp, floor=floor, wall=wall)
            # Send the commands to TDW in order to play the audio.
            resp = self.communicate(commands)

    def run(self):
        self.start()

        # Run a series of trials.
        for j in range(5):
            self.trial()

        # Terminate the build.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    ImpactSounds().run()
