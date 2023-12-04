# AUTOGENERATED FROM C#. DO NOT MODIFY.

from typing import Dict, List
from tdw.webgl.trials.trial import Trial


class TwoObjects(Trial):
    """
    An example demo scene. The user can move the camera with arrow keys. UI text will display user input and whether the user is mousing over an object.
    """

    def __init__(self, scene: str = "box_room_2018", avatar_position: Dict[str, float] = None, object_names: List[str] = None, object_positions: List[Dict[str, float]] = None, object_scale: float = 1, font_size: int = 24, font_color: Dict[str, float] = None, framerate: int = 60, render_quality: int = 5):
        """
        :param scene: The name of the scene.
        :param avatar_position: The initial position of the avatar.
        :param object_names: The name of the objects.
        :param object_positions: The positions of the objects.
        :param object_scale: Scale the objects uniformly by this factor.
        :param font_size: The UI text font size.
        :param font_color: The UI text font color.
        :param framerate: The target framerate.
        :param render_quality: The render quality (0 to 5, where 5 is best).
        """

        super().__init__(framerate=framerate, render_quality=render_quality)
        """:field
        The name of the scene.
        """
        self.scene: str = scene
        if avatar_position is None:
            """:field
            The initial position of the avatar.
            """
            self.avatar_position: Dict[str, float] = {"x": 3, "y": 0, "z": 1.25}
        else:
            self.avatar_position = avatar_position
        if object_names is None:
            """:field
            The name of the objects.
            """
            self.object_names: List[str] = ["chair_billiani_doll", "easter4"]
        else:
            self.object_names = object_names
        if object_positions is None:
            """:field
            The positions of the objects.
            """
            self.object_positions: List[Dict[str, float]] = [{"x": -2, "y": 0, "z": 2.3}, {"x": 2, "y": 0, "z": 2.3}]
        else:
            self.object_positions = object_positions
        """:field
        Scale the objects uniformly by this factor.
        """
        self.object_scale: float = object_scale
        """:field
        The UI text font size.
        """
        self.font_size: int = font_size
        if font_color is None:
            """:field
            The UI text font color.
            """
            self.font_color: Dict[str, float] = {"r": 1, "g": 0, "b": 0, "a": 1}
        else:
            self.font_color = font_color
