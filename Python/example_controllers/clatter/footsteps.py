from base64 import b64encode
from random import uniform
from subprocess import run, PIPE
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Transforms
from tdw.add_ons.cinematic_camera import CinematicCamera
from tdw.add_ons.audio_initializer import AudioInitializer

"""
Add a CinematicCamera and a non-physics humanoid to a streamed scene. Use Clatter to generate footsteps audio while the camera tracks the humanoid. To run this, you must add the Clatter CLI executable to the same directory as this script.
"""

c = Controller()
humanoid_id = c.get_unique_id()
initial_humanoid_position = np.array([9.03, -3, -4.57])
# Initialize the camera and audio.
initial_camera_position = np.array([initial_humanoid_position[0] + -2, 1.6, initial_humanoid_position[2] + 1])
camera = CinematicCamera(position=TDWUtils.array_to_vector3(initial_camera_position),
                         look_at=humanoid_id,
                         move_speed=0.0125)
audio = AudioInitializer(avatar_id=camera.avatar_id)
c.add_ons.extend([camera, audio])
# Get the non-physics humanoid.
animation_name = "walk_forward"
humanoid_animation_command, humanoid_animation_record = c.get_add_humanoid_animation(humanoid_animation_name=animation_name,
                                                                                     library="smpl_animations.json")
# Initialize the scene and start the animation.
resp = c.communicate([c.get_add_scene(scene_name="downtown_alleys"),
                      c.get_add_humanoid(humanoid_name="woman_business_1",
                                         object_id=humanoid_id,
                                         position=TDWUtils.array_to_vector3(initial_humanoid_position)),
                      humanoid_animation_command,
                      {"$type": "play_humanoid_animation",
                       "name": animation_name,
                       "id": humanoid_id,
                       "framerate": 60},
                      {"$type": "send_humanoids",
                       "frequency": "always"},
                      {"$type": "set_screen_size",
                       "width": 512,
                       "height": 512}])
# Move the camera to follow the humanoid.
camera.move_to_object(target=humanoid_id, offset={"x": -0.7, "y": 0.5, "z": 0})
# Run the simulation loop.
frame = 0
for i in range(300):
    frame += 1
    commands = []
    if frame % humanoid_animation_record.framerate == 0:
        # Restart the animation.
        commands.append({"$type": "play_humanoid_animation",
                         "name": animation_name,
                         "id": humanoid_id})
    if frame % 16 == 0:
        foot_position = Transforms(resp[0]).get_position(0)
        foot_position[1] = -3
        # This is approximately how far the foot is from the root body.
        foot_position[2] += 0.3
        # Generate an impact sound.
        resp = run(['./clatter.exe',
                    '--primary_material', 'wood_soft_1',
                    '--primary_amp', '0.1',
                    '--primary_resonance', '0.1',
                    '--primary_mass', '64',
                    '--secondary_material', 'stone_4',
                    '--secondary_amp', '0.5',
                    '--secondary_resonance', '0.01',
                    '--secondary_mass', '100',
                    '--speed', str(round(uniform(-1.6, -1.4))),
                    '--type', 'impact'],
                   check=True,
                   stdout=PIPE)
        # Encode the sound to a base64 string.
        audio = b64encode(resp.stdout).decode('utf-8')
        # Send a command to play the audio.
        commands.append({"$type": "play_audio_data",
                         "id": frame,
                         "position": TDWUtils.array_to_vector3(foot_position),
                         "wav_data": audio,
                         "num_frames": len(resp.stdout) // 2})
    resp = c.communicate(commands)
c.communicate({"$type": "terminate"})
