from random import uniform
from typing import List
from math import radians, sin, cos
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller
from tdw.output_data import Transforms
from tdw.add_ons.py_impact import PyImpact
from tdw.add_ons.cinematic_camera import CinematicCamera
from tdw.add_ons.audio_initializer import AudioInitializer

"""
Add a cinematic camera and a non-physics humanoid to a streamed scene.
Use PyImpact to generate footsteps audio while the camera tracks the humanoid.
"""

c = Controller()
humanoid_id = c.get_unique_id()
initial_humanoid_position = np.array([9.03, -3, -4.57])
# Initialize PyImpact but DON'T append it to the controller. We only want to use its lower-level API.
py_impact = PyImpact(initial_amp=0.9)
# Initialize the camera and audio.
initial_camera_position = np.array([initial_humanoid_position[0] + -2, 1.6, initial_humanoid_position[2] + 1])
camera = CinematicCamera(position=TDWUtils.array_to_vector3(initial_camera_position),
                         look_at=humanoid_id,
                         move_speed=0.0125)
audio = AudioInitializer(avatar_id=camera.avatar_id)
c.add_ons.extend([camera, audio])
animation_name = "walk_forward"
humanoid_animation_command, humanoid_animation_record = c.get_add_humanoid_animation(humanoid_animation_name=animation_name,
                                                                                     library="smpl_animations.json")
framerate = 60
resp = c.communicate([c.get_add_scene(scene_name="downtown_alleys"),
                      c.get_add_humanoid(humanoid_name="woman_business_1",
                                         object_id=humanoid_id,
                                         position=TDWUtils.array_to_vector3(initial_humanoid_position)),
                      humanoid_animation_command,
                      {"$type": "play_humanoid_animation",
                       "name": animation_name,
                       "id": humanoid_id,
                       "framerate": framerate},
                      {"$type": "set_target_framerate",
                       "framerate": framerate},
                      {"$type": "send_humanoids",
                       "frequency": "always"},
                      {"$type": "set_screen_size",
                       "width": 512,
                       "height": 512}])
camera.move_to_object(target=humanoid_id, offset={"x": -0.7, "y": 0.5, "z": 0})
frame = 0
for i in range(300):
    frame += 1
    commands = []
    if frame % humanoid_animation_record.framerate == 0:
        commands.append({"$type": "play_humanoid_animation",
                         "name": animation_name,
                         "id": humanoid_id})
    if frame % 16 == 0:
        foot_position = Transforms(resp[0]).get_position(0)
        foot_position[1] = -3
        # This is approximately how far the foot is from the root body.
        foot_position[2] += 0.3
        d_theta = int(360 / 3)
        r = 0.0625
        theta = 0
        contact_points: List[np.array] = list()
        contact_normals: List[np.array] = list()
        while theta < 360:
            rad = radians(theta)
            x = cos(rad) * r + foot_position[0]
            z = sin(rad) * r + foot_position[2]
            contact_points.append(np.array([x, -3, z]))
            contact_normals.append(np.array([0, 1, 0]))
            theta += d_theta
        commands.append(py_impact.get_impact_sound_command(velocity=np.array([0, uniform(-1.6, -1.4), 0]),
                                                           contact_points=contact_points,
                                                           contact_normals=contact_normals,
                                                           primary_id=humanoid_id,
                                                           primary_material="wood_soft_1",
                                                           primary_amp=0.1,
                                                           primary_mass=64,
                                                           secondary_id=None,
                                                           secondary_material="stone_4",
                                                           secondary_amp=0.5,
                                                           secondary_mass=100,
                                                           primary_resonance=0.1,
                                                           secondary_resonance=0.01))
    resp = c.communicate(commands)
c.communicate({"$type": "terminate"})
