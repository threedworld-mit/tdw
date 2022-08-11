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

    def __init__(self, hdri_skybox: str = None, rng: np.random.RandomState = None, aperture: float = 8,
                 focus_distance: float = 2.5, ambient_occlusion_intensity: float = 0.125,
                 ambient_occlusion_thickness_modifier: float = 3.5, shadow_strength: float = 1):
        """
        :param hdri_skybox: The name of the HDRI skybox. If None, a random skybox will be selected.
        :param rng: The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed.
        :param aperture: The depth-of-field aperture.
        :param focus_distance: The depth-of-field focus distance.
        :param ambient_occlusion_intensity: The intensity (darkness) of the Ambient Occlusion effect.
        :param ambient_occlusion_thickness_modifier: The thickness modifier for the Ambient Occlusion effect; controls "spread" of the effect out from corners.
        :param shadow_strength: The shadow strength of all lights in the scene.
        """

        super().__init__()
        """:field
        The name of the current HDRI skybox.
        """
        self.hdri_skybox: str = InteriorSceneLighting._get_hdri_skybox(hdri_skybox=hdri_skybox, rng=rng)
        self._aperture: float = aperture
        self._focus_distance: float = focus_distance
        self._ambient_occulsion_intensity: float = ambient_occlusion_intensity
        self._ambient_occlusion_thickness_modifier: float = ambient_occlusion_thickness_modifier
        self._shadow_strength: float = shadow_strength

    def get_initialization_commands(self) -> List[dict]:
        return [Controller.get_add_hdri_skybox(skybox_name=self.hdri_skybox),
                {'$type': 'set_render_quality',
                 'render_quality': 5},
                {'$type': 'set_aperture',
                 'aperture': self._aperture},
                {'$type': 'set_focus_distance',
                 'focus_distance': self._focus_distance},
                {'$type': 'set_post_exposure',
                 'post_exposure': InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES[self.hdri_skybox]},
                {'$type': 'set_ambient_occlusion_intensity',
                 'intensity': self._ambient_occulsion_intensity},
                {'$type': 'set_ambient_occlusion_thickness_modifier',
                 'thickness': self._ambient_occlusion_thickness_modifier},
                {'$type': 'set_shadow_strength',
                 'strength': self._shadow_strength}]

    def on_send(self, resp: List[bytes]) -> None:
        pass

    def reset(self, hdri_skybox: str = None, rng: np.random.RandomState = None, aperture: float = 8,
              focus_distance: float = 2.5, ambient_occlusion_intensity: float = 0.125,
              ambient_occlusion_thickness_modifier: float = 3.5, shadow_strength: float = 1):
        """
        Reset the HDRI skybox. Call this when resetting a scene.

        :param hdri_skybox: The name of the HDRI skybox. If None, a random skybox will be selected.
        :param rng: The random number generator for the purpose of selecting a random HDRI skybox. If None, a new random number generator will be created as needed.
        :param aperture: The depth-of-field aperture.
        :param focus_distance: The depth-of-field focus distance.
        :param ambient_occlusion_intensity: The intensity (darkness) of the Ambient Occlusion effect.
        :param ambient_occlusion_thickness_modifier: The thickness modifier for the Ambient Occlusion effect; controls "spread" of the effect out from corners.
        :param shadow_strength: The shadow strength of all lights in the scene.
        """

        self.initialized = False
        self.hdri_skybox = InteriorSceneLighting._get_hdri_skybox(hdri_skybox=hdri_skybox, rng=rng)
        self._aperture = aperture
        self._focus_distance = focus_distance
        self._ambient_occulsion_intensity = ambient_occlusion_intensity
        self._ambient_occlusion_thickness_modifier = ambient_occlusion_thickness_modifier
        self._shadow_strength = shadow_strength

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
                rng: np.random.RandomState = np.random.RandomState()
            return rng.choice(list(InteriorSceneLighting.SKYBOX_NAMES_AND_POST_EXPOSURE_VALUES.keys()))
