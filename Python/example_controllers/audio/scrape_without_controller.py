from typing import List, Optional
import numpy as np
from tdw.add_ons.py_impact import PyImpact
from tdw.physics_audio.base64_sound import Base64Sound
from tdw.physics_audio.scrape_material import ScrapeMaterial
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Make sounds with PyImpact without using a TDW controller.
"""

py_impact = PyImpact()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape_without_controller")
if not output_directory.exists():
    output_directory.mkdir()
print(f"Audio will be saved to: {output_directory}")
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
for i in range(5):
    sound: Optional[Base64Sound] = None
    for j in range(5):
        s = py_impact.get_scrape_sound(velocity=np.array([1.5, 0, 0]),
                                       contact_normals=contact_normals,
                                       primary_id=0,
                                       primary_material="metal_1",
                                       primary_amp=0.2,
                                       primary_mass=1,
                                       secondary_id=1,
                                       secondary_material="stone_4",
                                       secondary_amp=0.5,
                                       secondary_mass=100,
                                       primary_resonance=0.2,
                                       secondary_resonance=0.1,
                                       scrape_material=ScrapeMaterial.ceramic)
        if sound is None:
            sound = s
        elif s is not None:
            sound.bytes += s.bytes
            sound.length += s.length
    sound.write(path=output_directory.joinpath(f"{i}.wav"))
