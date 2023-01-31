from pkg_resources import resource_filename
from json import loads
from pathlib import Path
from typing import List, Dict
from tdw.physics_audio.scrape_sub_object import ScrapeSubObject
from tdw.physics_audio.scrape_material import ScrapeMaterial


class ScrapeModel:
    """
    Data for a 3D model being used as a Clatter scrape surface.
    """

    def __init__(self, model_name: str, sub_objects: List[ScrapeSubObject], visual_material: str,
                 scrape_material: ScrapeMaterial):
        """
        :param model_name: The name of the model.
        :param sub_objects: A list of [sub-objects that will be used as scrape surfaces](scrape_sub_object.md).
        :param visual_material: The name of the new visual material.
        :param scrape_material: The [scrape material](scrape_material.md).
        """

        """:field
        The name of the model.
        """
        self.model_name: str = model_name
        """:field
        A list of [sub-objects that will be used as scrape surfaces](scrape_sub_object.md).
        """
        self.sub_objects: List[ScrapeSubObject] = sub_objects
        """:field
        The [scrape material](scrape_material.md).
        """
        self.scrape_material: ScrapeMaterial = scrape_material
        """:field
        The name of the new visual material.
        """
        self.visual_material: str = visual_material


def __get_default_scrape_models() -> Dict[str, ScrapeModel]:
    """
    :return: A dictionary of default scrape model data.
    """

    scrape_models: Dict[str, ScrapeModel] = dict()
    default_scrape_materials: Dict[str, Dict[str, str]] = loads(
        Path(resource_filename(__name__, f"scrape_materials.json")).read_text())
    default_scrape_models: Dict[str, dict] = loads(
        Path(resource_filename(__name__, f"scrape_models.json")).read_text())
    for model_name in default_scrape_models:
        visual_material = default_scrape_models[model_name]["visual_material"]
        sub_objects: List[ScrapeSubObject] = list()
        for sub_object in default_scrape_models[model_name]["sub_objects"]:
            sub_objects.append(ScrapeSubObject(name=sub_object["name"],
                                               material_index=sub_object["material_index"]))
        scrape_material = ScrapeMaterial[default_scrape_materials[visual_material]["scrape_material"]]
        scrape_models[model_name] = ScrapeModel(model_name=model_name,
                                                sub_objects=sub_objects,
                                                visual_material=visual_material,
                                                scrape_material=scrape_material)
    return scrape_models


DEFAULT_SCRAPE_MODELS: Dict[str, ScrapeModel] = __get_default_scrape_models()
