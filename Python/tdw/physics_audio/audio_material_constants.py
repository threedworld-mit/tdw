from typing import Dict
from tdw.physics_audio.audio_material import AudioMaterial


# Density per audio material.
DENSITIES: Dict[AudioMaterial, float] = {AudioMaterial.ceramic: 2180,
                                         AudioMaterial.glass: 2500,
                                         AudioMaterial.stone: 2000,
                                         AudioMaterial.metal: 8450,
                                         AudioMaterial.wood_hard: 1200,
                                         AudioMaterial.wood_medium: 700,
                                         AudioMaterial.wood_soft: 400,
                                         AudioMaterial.fabric: 1540,
                                         AudioMaterial.leather: 860,
                                         AudioMaterial.plastic_hard: 1150,
                                         AudioMaterial.plastic_soft_foam: 285,
                                         AudioMaterial.rubber: 1522,
                                         AudioMaterial.paper: 1200,
                                         AudioMaterial.cardboard: 698}
# Dynamic friction per audio material.
DYNAMIC_FRICTION: Dict[AudioMaterial, float] = {AudioMaterial.ceramic: 0.47,
                                                AudioMaterial.wood_hard: 0.35,
                                                AudioMaterial.wood_medium: 0.35,
                                                AudioMaterial.wood_soft: 0.35,
                                                AudioMaterial.cardboard: 0.45,
                                                AudioMaterial.paper: 0.47,
                                                AudioMaterial.glass: 0.65,
                                                AudioMaterial.fabric: 0.65,
                                                AudioMaterial.leather: 0.4,
                                                AudioMaterial.stone: 0.7,
                                                AudioMaterial.rubber: 0.75,
                                                AudioMaterial.plastic_hard: 0.3,
                                                AudioMaterial.plastic_soft_foam: 0.45,
                                                AudioMaterial.metal: 0.43}
# Static friction per audio material.
STATIC_FRICTION: Dict[AudioMaterial, float] = {AudioMaterial.ceramic: 0.47,
                                               AudioMaterial.wood_hard: 0.37,
                                               AudioMaterial.wood_medium: 0.37,
                                               AudioMaterial.wood_soft: 0.37,
                                               AudioMaterial.cardboard: 0.48,
                                               AudioMaterial.paper: 0.5,
                                               AudioMaterial.glass: 0.68,
                                               AudioMaterial.fabric: 0.67,
                                               AudioMaterial.leather: 0.43,
                                               AudioMaterial.stone: 0.72,
                                               AudioMaterial.rubber: 0.8,
                                               AudioMaterial.plastic_hard: 0.35,
                                               AudioMaterial.plastic_soft_foam: 0.47,
                                               AudioMaterial.metal: 0.47}
