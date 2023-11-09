from typing import List, Tuple, Dict, Optional
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.add_ons.mouse import Mouse
from tdw.add_ons.ui_widgets.timer_bar import TimerBar
from tdw.add_ons.trials.trial import Trial
from tdw.add_ons.trials.trial_status import TrialStatus
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


class Ninja(Trial):
    """
    Objects appear on the screen and start moving.

    The trial fails if the user clicks the wrong object or time runs out.

    The trial succeeds if the user clicks the correct (target) object.
    """

    # The ID of the target object.
    _TARGET_OBJECT_ID: int = 0
    # The camera field of view. This is used to place objects in a viewable position.
    _FIELD_OF_VIEW: float = 54.43223
    """:class_var
    If `scene_names = None` in the constructor, this is the default list of possible scene names.
    """
    DEFAULT_SCENES_NAMES: List[str] = ["tdw_room", "box_room_2018"]
    """:class_var
    If `model_names = None` in the constructor, this is the default list of possible model names.
    """
    DEFAULT_MODEL_NAMES: List[str] = ["bowl", "cone", "cube", "pyramid", "torus"]
    """:class_var
    If `target_object_names = None` in the constructor, this is the default list of possible target object names.
    """
    DEFAULT_TARGET_OBJECT_NAMES: List[str] = ["sphere"]

    def __init__(self, random_seed: int = None, delay_at_start: float = 2, time: float = 5,
                 scene_names: List[str] = None, model_names: List[str] = None, target_object_names: List[str] = None,
                 scale_range: Tuple[float, float] = (0.15, 0.3), speed_range: Tuple[float, float] = (0.5, 1.5),
                 distance_range: Tuple[float, float] = (3, 4), mass_range: Tuple[float, float] = (0.5, 1),
                 dynamic_friction_range: Tuple[float, float] = (0.2, 0.9),
                 static_friction_range: Tuple[float, float] = (0.2, 0.9),
                 bounciness_range: Tuple[float, float] = (0.2, 0.9),
                 num_objects_range: Tuple[int, int] = (5, 15),
                 randomize_colors: bool = True, avatar_height: float = 1.8, gravity: float = -2,
                 library: str = "models_flex.json"):
        """
        :param random_seed: The random seed. Can be null. If null, the seed is random.
        :param delay_at_start: Wait this many seconds at the start of the simulation before objects start moving, time starts decrementing, and user input is allowed.
        :param time: The total time in seconds that the user has to click the target object.
        :param scene_names: An array of scene names. A random scene will be chosen from this array per trial.
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
        :param library: The model library.
        """

        if random_seed is not None:
            np.random.seed(random_seed)
        # This is used to detect mouse input.
        self._mouse: Mouse = Mouse()
        # This is used to track time.
        self._timer_bar: TimerBar = TimerBar(total_time=time)
        super().__init__()
        self.delay_at_start: float = delay_at_start
        if scene_names is None:
            self.scene_names: List[str] = Ninja.DEFAULT_SCENES_NAMES[:]
        else:
            self.scene_names = scene_names[:]
        if model_names is None:
            self.model_names = Ninja.DEFAULT_MODEL_NAMES[:]
        else:
            self.model_names = model_names[:]

        # Set a random target object.
        if target_object_names is None:
            target_object_names = Ninja.DEFAULT_TARGET_OBJECT_NAMES[:]
        self._target_object_name: str = target_object_names[np.random.randint(0, len(target_object_names))]

        self._scale_range: Tuple[float, float] = scale_range
        self._speed_range: Tuple[float, float] = speed_range
        self._distance_range: Tuple[float, float] = distance_range
        self._mass_range: Tuple[float, float] = mass_range
        self._dynamic_friction_range: Tuple[float, float] = dynamic_friction_range
        self._static_friction_range: Tuple[float, float] = static_friction_range
        self._bounciness_range: Tuple[float, float] = bounciness_range
        self._num_objects_range: Tuple[int, int] = num_objects_range
        self._randomize_colors: bool = randomize_colors
        self._gravity: float = gravity
        self._avatar_position: np.ndarray = np.array([0, avatar_height, -1.5])
        self._library: str = library
        self._colors: Dict[str, Dict[str, float]] = dict()
        self._clicked_object: Optional[int] = None

    def _get_instructions(self) -> str:
        return f"Click on the {self._target_object_name}"

    def _get_add_ons(self) -> List[AddOn]:
        return [self._mouse, self._timer_bar]

    def _get_trial_initialization_commands(self) -> List[dict]:
        # Add the scene. Set gravity.
        commands = [Controller.get_add_scene(scene_name=self.scene_names[np.random.randint(0, len(self.scene_names))]),
                    {"$type": "set_gravity_vector",
                     "gravity": {"x": 0, "y": self._gravity, "z": 0}}]
        # Add the avatar.
        commands.extend(TDWUtils.create_avatar(position=TDWUtils.array_to_vector3(self._avatar_position)))
        # Add the target object.
        positions: List[np.ndarray] = list()
        object_id = self._add_object(commands=commands,
                                     name=self._target_object_name,
                                     positions=positions,
                                     object_id=Ninja._TARGET_OBJECT_ID)

        # Add other objects.
        num_objects: int = int(np.random.randint(self._num_objects_range[0], self._num_objects_range[1]))
        for i in range(num_objects):
            object_id = self._add_object(commands=commands,
                                         name=self.model_names[np.random.randint(0, len(self.model_names))],
                                         positions=positions,
                                         object_id=object_id)
        # Send avatar data for only this frame. Send transforms data per-frame.
        commands.extend([{"$type": "send_avatars",
                          "frequency": "once"},
                         {"$type": "send_transforms",
                          "frequency": "always"}])
        return commands

    def _update_trial(self, resp: List[bytes]) -> None:
        # Start the timer.
        if not self._timer_bar.started:
            self._timer_bar.start()
        # The user clicked an object.
        if self._mouse.left_button_pressed and self._mouse.mouse_is_over_object:
            self._clicked_object = self._mouse.mouse_over_object_id

    def _get_trial_status(self, resp: List[bytes]) -> TrialStatus:
        if self._clicked_object is not None:
            if self._clicked_object == Ninja._TARGET_OBJECT_ID:
                return TrialStatus.success
            else:
                return TrialStatus.failure
        elif self._timer_bar.done:
            return TrialStatus.failure
        else:
            return TrialStatus.running

    def _add_object(self, commands: List[dict], name: str, positions: List[np.ndarray], object_id: int) -> int:
        """
        Add an object into the scene. Set a random color and velocity.

        The object's position is random but in range of the camera and away from other objects.
        The object's physics values, scale, and speed are random within a range.
        The object's rotation is random.

        :param commands: The list of commands.
        :param name: The name of the model.
        :param positions: The positions of the models that we've already added. This will be added to.
        :param object_id: This object's ID. This will be incremented.

        :return: The next object ID.
        """

        # Try to get a random position that isn't too close to the other positions we've already set.
        position: np.ndarray = np.zeros(3)
        got_position: bool = False
        r = self._scale_range[1] / 2
        for i in range(1000):
            # Get the z coordinate from the distance.
            z = self._avatar_position[2] + np.random.uniform(self._distance_range[0], self._distance_range[1])
            # Derive the maximum x coordinate.
            x1 = np.tan(np.deg2rad(Ninja._FIELD_OF_VIEW / 2)) * z
            # Get the x coordinate.
            x = np.random.uniform(-x1, x1)
            # The y coordinate is more random.
            y = np.random.uniform(0.2, 2)
            position = np.array([x, y, z])
            if len(positions) == 0:
                got_position = True
            else:
                # This position can't be too close to the other positions.
                for p in positions:
                    if np.linalg.norm(position - p) > r:
                        got_position = True
                        break
            if got_position:
                break
        if not got_position:
            return object_id

        # Get random physics values.
        mass = float(np.random.uniform(self._mass_range[0], self._mass_range[1]))
        dynamic_friction = float(np.random.uniform(self._dynamic_friction_range[0], self._dynamic_friction_range[1]))
        static_friction = float(np.random.uniform(self._static_friction_range[0], self._static_friction_range[1]))
        bounciness = float(np.random.uniform(self._bounciness_range[0], self._bounciness_range[1]))

        # Get a random scale.
        s = float(np.random.uniform(self._scale_range[0], self._scale_range[1]))
        scale_factor = {"x": s, "y": s, "z": s}

        # Add the object.
        commands.extend(Controller.get_add_physics_object(model_name=name,
                                                          object_id=object_id,
                                                          position=TDWUtils.array_to_vector3(position),
                                                          rotation=TDWUtils.array_to_vector3(np.random.uniform(-360, 360, 3)),
                                                          scale_factor=scale_factor,
                                                          scale_mass=False,
                                                          default_physics_values=False,
                                                          mass=mass,
                                                          dynamic_friction=dynamic_friction,
                                                          static_friction=static_friction,
                                                          bounciness=bounciness,
                                                          library=self._library))
        commands.append({"$type": "set_object_collision_detection_mode",
                         "id": object_id,
                         "mode": "discrete"})

        # Set the object's color.
        if self._randomize_colors:
            # Add a color.
            if name not in self._colors:
                self._colors[name] = TDWUtils.array_to_color(np.random.random(4))
                self._colors[name]["a"] = 1
            commands.append({"$type": "set_color",
                             "id": object_id,
                             "color": self._colors[name]})

        # Set a random velocity.
        velocity: np.ndarray = np.random.random(3) * np.random.uniform(self._speed_range[0], self._speed_range[1])
        # Go up.
        velocity[1] = abs(velocity[1])
        # Go towards the center of the screen.
        if velocity[0] < 0 and position[0] < 0:
            velocity[0] = abs(velocity[0])
        elif velocity[0] > 0 and position[0] > 0:
            velocity[0] = -velocity[0]
        # Go towards the avatar.
        if velocity[2] > 0:
            velocity[2] = -velocity[2]
        commands.append({"$type": "set_velocity",
                         "id": object_id,
                         "velocity": TDWUtils.array_to_vector3(velocity)})

        # Add the position.
        positions.append(position)
        # Increment the object ID.
        return object_id + 1
