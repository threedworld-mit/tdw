from typing import List
import numpy as np
from tdw.add_ons.py_impact import PyImpact
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Generate impact sounds with PyImpact without using a TDW controller and save them to disk.
"""

py_impact = PyImpact()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("impact_without_controller")
if not output_directory.exists():
    output_directory.mkdir()
print(f"Audio will be saved to: {output_directory}")
contact_normals: List[np.array] = list()
for i in range(3):
    contact_normals.append(np.array([0, 1, 0]))
for i in range(5):
    sound = py_impact.get_impact_sound(velocity=np.array([0, -1.5, 0]),
                                       contact_normals=contact_normals,
                                       primary_id=0,
                                       primary_material="metal_1",
                                       primary_amp=0.2,
                                       primary_mass=1,
                                       secondary_id=None,
                                       secondary_material="stone_4",
                                       secondary_amp=0.5,
                                       secondary_mass=100,
                                       primary_resonance=0.2,
                                       secondary_resonance=0.1)
    sound.write(path=output_directory.joinpath(f"{i}.wav"))
    py_impact.reset()
