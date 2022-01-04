from time import sleep
from typing import List
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.resonance_audio_initializer import ResonanceAudioInitializer
from tdw.add_ons.py_impact import PyImpact
from tdw.audio_utils import AudioUtils
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Generate scrape sounds with PyImpact without using physics data and play the audio in a circle around the avatar listener.
"""

c = Controller()
# Add a camera and initialize audio.
y = 2
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": y, "z": 0})
resonance_audio_floor = "metal"
resonance_audio_wall = "brick"
resonance_audio_ceiling = "acousticTile"
audio = ResonanceAudioInitializer(avatar_id="a",
                                  floor=resonance_audio_floor,
                                  front_wall=resonance_audio_wall,
                                  back_wall=resonance_audio_wall,
                                  left_wall=resonance_audio_wall,
                                  right_wall=resonance_audio_wall,
                                  ceiling=resonance_audio_ceiling)
c.add_ons.extend([camera, audio])

# Initialize the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))

# Initialize PyImpact but DON'T add it as an add-on.
py_impact_floor = ResonanceAudioInitializer.AUDIO_MATERIALS[resonance_audio_floor]
impact_sound_floor = py_impact_floor.name + "_4"
py_impact = PyImpact(initial_amp=0.9, floor=py_impact_floor, resonance_audio=True, rng=np.random.RandomState(0))

# Generate contact normals and set the collision velocity.
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
velocity = np.array([1.5, 0, 0])

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape_with_controller/audio.wav")
print(f"Audio will be saved to: {path}")
if not path.parent.exists():
    path.parent.mkdir(parents=True)
AudioUtils.start(output_path=path)
# Add sounds in a circle around the avatar.
distance = 1.5
theta = 0
d_theta = 15
contact_radius = 0.0625
while theta < 360:
    # Get the position of the sound.
    rad = np.radians(theta)
    x = np.cos(rad) * distance
    z = np.sin(rad) * distance
    # Generate contact points around the sound's position.
    contact_points: List[np.array] = list()
    contact_angle = 0
    for i in range(3):
        r = np.radians(contact_angle)
        contact_x = np.cos(r) * contact_radius + x
        contact_z = np.sin(r) * contact_radius + z
        contact_points.append(np.array([contact_x, y, contact_z]))

    # Get a sound.
    for i in range(5):
        c.communicate(py_impact.get_scrape_sound_command(velocity=velocity,
                                                         contact_points=contact_points,
                                                         contact_normals=contact_normals,
                                                         primary_id=0,
                                                         primary_material="metal_1",
                                                         primary_amp=0.4,
                                                         primary_mass=4,
                                                         secondary_id=None,
                                                         secondary_material="ceramic_4",
                                                         secondary_amp=0.5,
                                                         secondary_mass=100,
                                                         primary_resonance=0.4,
                                                         secondary_resonance=0.2,
                                                         scrape_material=ScrapeMaterial.ceramic))
        py_impact.reset()
    sleep(0.15)
    theta += d_theta
sleep(0.15)
AudioUtils.stop()
c.communicate({"$type": "terminate"})
