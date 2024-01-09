# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.webgl.trials.trial import Trial
from typing import List


class Ninja(Trial):
    """
    Random objects appear in front of the camera at random trajectories.
    """

    def __init__(self, random_seed: int = None, time: float = 5, scene_name: str = "tdw_room", model_names: List[str] = None, target_object_names: List[str] = None, scale_range: List[float] = None, speed_range: List[float] = None, distance_range: List[float] = None, mass_range: List[float] = None, dynamic_friction_range: List[float] = None, static_friction_range: List[float] = None, bounciness_range: List[float] = None, num_objects_range: List[int] = None, randomize_colors: bool = True, avatar_height: float = 1.8, gravity: float = -2):
        """
        :param random_seed: The random seed. Can be null. If null, the seed is random.
        :param time: The total time in seconds that the user has to click the target object.
        :param scene_name: The name of the scene.
        :param model_names: The names of the models that aren't target objects.
        :param target_object_names: The names of all possible target objects.
        :param scale_range: Each model will be scaled to a random factor within this range (min, max).
        :param speed_range: Each model's initial speed will be a random value within this range (min, max).
        :param distance_range: Each model will be at a random distance within this range (min, max) from the camera.
        :param mass_range: Each model will have a mass within this range (min, max).
        :param dynamic_friction_range: Each model will have a dynamic friction value within this range (min, max).
        :param static_friction_range: Each model will have a static friction value within this range (min, max).
        :param bounciness_range: Each model will have a bounciness value within this range (min, max).
        :param num_objects_range: Each trial will have a number of objects within this range (min, max).
        :param randomize_colors: If true, the color of each model (not each object instance) will be random.
        :param avatar_height: The height of the avatar (camera).
        :param gravity: The speed of gravity.
        """

        super().__init__()
        """:field
        The random seed. Can be null. If null, the seed is random.
        """
        self.random_seed: int = random_seed
        """:field
        The total time in seconds that the user has to click the target object.
        """
        self.time: float = time
        """:field
        The name of the scene.
        """
        self.scene_name: str = scene_name
        if model_names is None:
            """:field
            The names of the models that aren't target objects.
            """
            self.model_names: List[str] = ["bowl", "cone", "cube", "pyramid", "torus"]
        else:
            self.model_names = model_names
        if target_object_names is None:
            """:field
            The names of all possible target objects.
            """
            self.target_object_names: List[str] = ["sphere"]
        else:
            self.target_object_names = target_object_names
        if scale_range is None:
            """:field
            Each model will be scaled to a random factor within this range (min, max).
            """
            self.scale_range: List[float] = [0.15, 0.3]
        else:
            self.scale_range = scale_range
        if speed_range is None:
            """:field
            Each model's initial speed will be a random value within this range (min, max).
            """
            self.speed_range: List[float] = [0.5, 1.5]
        else:
            self.speed_range = speed_range
        if distance_range is None:
            """:field
            Each model will be at a random distance within this range (min, max) from the camera.
            """
            self.distance_range: List[float] = [3, 4]
        else:
            self.distance_range = distance_range
        if mass_range is None:
            """:field
            Each model will have a mass within this range (min, max).
            """
            self.mass_range: List[float] = [0.5, 1]
        else:
            self.mass_range = mass_range
        if dynamic_friction_range is None:
            """:field
            Each model will have a dynamic friction value within this range (min, max).
            """
            self.dynamic_friction_range: List[float] = [0.2, 0.9]
        else:
            self.dynamic_friction_range = dynamic_friction_range
        if static_friction_range is None:
            """:field
            Each model will have a static friction value within this range (min, max).
            """
            self.static_friction_range: List[float] = [0.2, 0.9]
        else:
            self.static_friction_range = static_friction_range
        if bounciness_range is None:
            """:field
            Each model will have a bounciness value within this range (min, max).
            """
            self.bounciness_range: List[float] = [0.2, 0.9]
        else:
            self.bounciness_range = bounciness_range
        if num_objects_range is None:
            """:field
            Each trial will have a number of objects within this range (min, max).
            """
            self.num_objects_range: List[int] = [5, 15]
        else:
            self.num_objects_range = num_objects_range
        """:field
        If true, the color of each model (not each object instance) will be random.
        """
        self.randomize_colors: bool = randomize_colors
        """:field
        The height of the avatar (camera).
        """
        self.avatar_height: float = avatar_height
        """:field
        The speed of gravity.
        """
        self.gravity: float = gravity