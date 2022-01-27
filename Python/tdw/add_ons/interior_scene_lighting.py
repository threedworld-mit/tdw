import numpy as np
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from typing import Dict, List
from tdw.add_ons.add_on import AddOn
from tdw.controller import Controller


class InteriorSceneLighting(AddOn):
    """
    Add an HDRI skybox to the scene from a curated list of skyboxes and set post-processing values.

    The list of skyboxes is a subset of all of the skyboxes available in TDW. They are all *exterior* skyboxes, which means that they are suitable for *interior* scenes such as `floorplan_1a` or `mm_craftroom_2b`. Note that some interior scenes are not HDRI-compatible; see `scene_record.hdri`.
    """

    """:class_var
    A dictionary of all of the possible HDRI skyboxes. Key = The HDRI skybox name. Value = the post exposure value.
    """
    SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES: Dict[str, float] = loads(Path(resource_filename(__name__, "interior_scene_lighting_data/hdri_skyboxes.json")).read_text())

    def __init__(self, hdri_skybox: str = None, rng: np.random.RandomState = None):
        """
        :param hdri_skybox: The name of the HDRI skybox. If None, a random skybox will be selected.
        :param rng: The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed.
        """

        super().__init__()
        """:field
        The name of the current HDRI skybox.
        """
        self.hdri_skybox: str = InteriorSceneLighting._get_hdri_skybox(hdri_skybox=hdri_skybox, rng=rng)

    def get_initialization_commands(self) -> List[dict]:
        return [Controller.get_add_hdri_skybox(skybox_name=self.hdri_skybox),
                {'$type': 'set_render_quality',
                 'render_quality': 5},
                {'$type': 'set_aperture',
                 'aperture': 8},
                {'$type': 'set_focus_distance',
                 'focus_distance': 2.5},
                {'$type': 'set_post_exposure',
                 'post_exposure': InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES[self.hdri_skybox]},
                {'$type': 'set_ambient_occlusion_intensity',
                 'intensity': 0.125},
                {'$type': 'set_ambient_occlusion_thickness_modifier',
                 'thickness': 3.5},
                {'$type': 'set_shadow_strength',
                 'strength': 1.0}]

    def on_send(self, resp: List[bytes]) -> None:
        pass

    def reset(self, hdri_skybox: str = None, rng: np.random.RandomState = None):
        """
        Reset the HDRI skybox. Call this when resetting a scene.

        :param hdri_skybox: The name of the HDRI skybox. If None, a random skybox will be selected.
        :param rng: The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed.
        """

        self.initialized = False
        self.hdri_skybox = InteriorSceneLighting._get_hdri_skybox(hdri_skybox=hdri_skybox, rng=rng)

    @staticmethod
    def _get_hdri_skybox(hdri_skybox: str, rng: np.random.RandomState) -> str:
        """
        :param hdri_skybox: The name of the HDRI skybox. If None, a random skybox will be selected.
        :param rng: The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed.

        :return: The name of the HDRI skybox.
        """

        if hdri_skybox is not None:
            assert hdri_skybox in InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES, f"Skybox {hdri_skybox} not found in InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES"
            return hdri_skybox
        else:
            if rng is None:
                rng = np.random.RandomState = np.random.RandomState()
            return rng.choice(list(InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES.keys()))
