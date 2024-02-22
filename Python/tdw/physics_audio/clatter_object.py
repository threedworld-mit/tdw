from typing import Optional
from tdw.physics_audio.impact_material import ImpactMaterial
from tdw.physics_audio.scrape_model import ScrapeModel


class ClatterObject:
    """
    Clatter audio object data.
    """

    def __init__(self, impact_material: ImpactMaterial, size: int, amp: float, resonance: float,
                 fake_mass: float = None, scrape_model: ScrapeModel = None, is_robot: bool = False):
        self.impact_material: ImpactMaterial = impact_material
        self.size: int = size
        self.amp: float = amp
        self.resonance: float = resonance
        self.fake_mass: Optional[float] = fake_mass
        self.scrape_model: Optional[ScrapeModel] = scrape_model
        self.is_robot: bool = is_robot
