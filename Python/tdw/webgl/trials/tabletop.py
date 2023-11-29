# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.webgl.trials.tabletop_base import TabletopBase
from typing import List, Dict
from tdw.cardinal_direction import CardinalDirection


class Tabletop(TabletopBase):
    """
    Add objects on the table including a target object. Add a first person avatar.
    """

    def __init__(self, avatar_directions: List[CardinalDirection] = None, avatar_distance: List[float] = None, avatar_perturbation: float = 0, avatar_rotation: float = 0, font_color: Dict[str, float] = None, font_size: int = 24, framerate: int = 60, model_names: List[str] = None, model_position_perturbation: float = 0.0125, model_position_step: float = 0.05, progress_bar_overlay_color: Dict[str, float] = None, progress_bar_size: Dict[str, int] = None, progress_bar_underlay_color: Dict[str, float] = None, random_seed: int = None, render_quality: int = 5, rotate_table: float = 0, scene_name: str = "box_room_2018", table_extents_factor: float = 0.85, table_names: List[str] = None, table_position_perturbation: float = 0, target_object_names: List[str] = None, target_object_ui_texts: List[str] = None, time: float = 30):
        """
        :param avatar_directions: The avatar can spawn at any of these compass directions from the table.
        :param avatar_distance: The avatar will initially be at a distance from the table defined by these two values (min, max).
        :param avatar_perturbation: The avatar's position will be perturbed by a factor between 0 and this value, in meters.
        :param avatar_rotation: When the avatar is spawned, it will look at the center of the table and then turn between -avatar_rotation and avatar_rotation degrees.
        :param font_color: The font color.
        :param font_size: The font size.
        :param framerate: The target framerate.
        :param model_names: A list of names of models that can be randomly added to the table.
        :param model_position_perturbation: Perturb each table position by this factor.
        :param model_position_step: Step each table position by this distance.
        :param progress_bar_overlay_color: The color of the progress bar overlay.
        :param progress_bar_size: The size of the progress bar in pixels.
        :param progress_bar_underlay_color: The color of the progress bar underlay.
        :param random_seed: The random seed. Can be null. If null, the seed is random.
        :param render_quality: The render quality (0 to 5, where 5 is best).
        :param rotate_table: A value between 0 and 1 that defines the probability that the table will be rotated 90 degrees.
        :param scene_name: The name of the scene.
        :param table_extents_factor: When adding objects, shrink the table extents by this factor to prevent objects from falling off.
        :param table_names: A list of names of table models. One of these will be randomly selected and added to the scene.
        :param table_position_perturbation: The table will be at a random position relative to (0, 0, 0). The position is calculated by getting a random position in a circle. The radius of the circle is between 0 and this value. Set this to 0 if you want the table to always be at (0, 0, 0).
        :param target_object_names: An array of target object model names. A random target object will be chosen from this array per trial.
        :param target_object_ui_texts: An array of target object model names as they will be displayed in UI text.
        :param time: The total time in seconds that the user has to click the object.
        """

        super().__init__(avatar_directions=avatar_directions, avatar_distance=avatar_distance, avatar_perturbation=avatar_perturbation, avatar_rotation=avatar_rotation, font_color=font_color, font_size=font_size, framerate=framerate, model_names=model_names, model_position_perturbation=model_position_perturbation, model_position_step=model_position_step, progress_bar_overlay_color=progress_bar_overlay_color, progress_bar_size=progress_bar_size, progress_bar_underlay_color=progress_bar_underlay_color, random_seed=random_seed, render_quality=render_quality, rotate_table=rotate_table, scene_name=scene_name, table_extents_factor=table_extents_factor, table_names=table_names, table_position_perturbation=table_position_perturbation, target_object_names=target_object_names, target_object_ui_texts=target_object_ui_texts, time=time)

