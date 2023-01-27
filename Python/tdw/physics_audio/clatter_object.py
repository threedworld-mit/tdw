import io
from csv import DictReader
from pathlib import Path
from typing import Optional, Dict
from pkg_resources import resource_filename
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


def __get_default_objects() -> Dict[str, ClatterObject]:
    """
    Returns default `ClatterObject` values. Not all objects have default values; more will be added in time.

    :return: A list of default `ClatterObject`. Key = the name of the model. Value = object info.
    """

    objects: Dict[str, ClatterObject] = {}
    # Load the objects.csv metadata file.
    csv_file = str(Path(resource_filename(__name__, f"objects.csv")).resolve())
    # Parse the .csv file.
    with io.open(csv_file, newline='', encoding='utf-8-sig') as f:
        reader = DictReader(f)
        for row in reader:
            objects[row["name"]] = ClatterObject(impact_material=ImpactMaterial[row["material"]],
                                                 size=int(row["size"]),
                                                 amp=float(row["amp"]),
                                                 resonance=float(row["resonance"]))
    return objects


DEFAULT_OBJECTS: Dict[str, ClatterObject] = __get_default_objects()
