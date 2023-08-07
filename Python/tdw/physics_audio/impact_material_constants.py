from typing import Dict
from tdw.physics_audio.impact_material import ImpactMaterial


# Density per impact material.
DENSITIES: Dict[ImpactMaterial, float] = {ImpactMaterial.ceramic: 2180,
                                          ImpactMaterial.glass: 2500,
                                          ImpactMaterial.stone: 2000,
                                          ImpactMaterial.metal: 8450,
                                          ImpactMaterial.wood_hard: 1200,
                                          ImpactMaterial.wood_medium: 700,
                                          ImpactMaterial.wood_soft: 400,
                                          ImpactMaterial.fabric: 1540,
                                          ImpactMaterial.leather: 860,
                                          ImpactMaterial.plastic_hard: 1150,
                                          ImpactMaterial.plastic_soft_foam: 285,
                                          ImpactMaterial.rubber: 1522,
                                          ImpactMaterial.paper: 1200,
                                          ImpactMaterial.cardboard: 698}
# Dynamic friction per impact material.
DYNAMIC_FRICTION: Dict[ImpactMaterial, float] = {ImpactMaterial.ceramic: 0.47,
                                                 ImpactMaterial.wood_hard: 0.35,
                                                 ImpactMaterial.wood_medium: 0.35,
                                                 ImpactMaterial.wood_soft: 0.35,
                                                 ImpactMaterial.cardboard: 0.45,
                                                 ImpactMaterial.paper: 0.47,
                                                 ImpactMaterial.glass: 0.65,
                                                 ImpactMaterial.fabric: 0.65,
                                                 ImpactMaterial.leather: 0.4,
                                                 ImpactMaterial.stone: 0.7,
                                                 ImpactMaterial.rubber: 0.75,
                                                 ImpactMaterial.plastic_hard: 0.3,
                                                 ImpactMaterial.plastic_soft_foam: 0.45,
                                                 ImpactMaterial.metal: 0.43}
# Static friction per impact material.
STATIC_FRICTION: Dict[ImpactMaterial, float] = {ImpactMaterial.ceramic: 0.47,
                                                ImpactMaterial.wood_hard: 0.37,
                                                ImpactMaterial.wood_medium: 0.37,
                                                ImpactMaterial.wood_soft: 0.37,
                                                ImpactMaterial.cardboard: 0.48,
                                                ImpactMaterial.paper: 0.5,
                                                ImpactMaterial.glass: 0.68,
                                                ImpactMaterial.fabric: 0.67,
                                                ImpactMaterial.leather: 0.43,
                                                ImpactMaterial.stone: 0.72,
                                                ImpactMaterial.rubber: 0.8,
                                                ImpactMaterial.plastic_hard: 0.35,
                                                ImpactMaterial.plastic_soft_foam: 0.47,
                                                ImpactMaterial.metal: 0.47}
