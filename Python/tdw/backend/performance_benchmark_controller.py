from typing import List, Tuple
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark


class PerformanceBenchmarkController(Controller):
    """
    Use this controller to create performance benchmarks.
    """
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        """:field
        The [`Benchmark`](../add_ons/benchmark.md) add-on.
        """
        self.benchmark: Benchmark = Benchmark()
        self.add_ons.append(self.benchmark)

    def run(self, boxes: bool = False, render_quality: int = 0, post_processing: bool = False,
            pass_masks: List[str] = None, png: bool = False, transforms: bool = False, rigidbodies: bool = False,
            collisions: bool = False, bounds: bool = False, screen_size: int = 256, junk: int = None,
            images: bool = False, id_colors: bool = False, collision_enter: bool = True, collision_exit: bool = True,
            collision_stay: bool = True, env_collisions: bool = True, occlusion: bool = False,
            num_frames: int = 5000) -> float:
        """
        Run a performance benchmark test.

        :param boxes: If True, add 100 cubes to the scene.
        :param render_quality: The render quality (0 to 5).
        :param post_processing: If True, enable post-processing.
        :param pass_masks: The pass masks.
        :param png: If True, encode the `_img` pass as a .png. If False, encode the `_img` pass as a .jpg. Ignored if `passes` doesn't include `_img` or if `images` is `False`.
        :param transforms: If True, send `Transforms` data per frame.
        :param rigidbodies: If True, send `Rigidbodies` data per frame.
        :param collisions: If True, send collision data per frame.
        :param bounds: If True, send `Bounds` data per frame.
        :param screen_size: The screen size in pixels.
        :param junk: If not None, request this much junk data per frame.
        :param images: If True, add an avatar and send `Images` data per frame.
        :param id_colors: If True, add an avatar and send `IdPassSegmentationColors` data per frame.
        :param collision_enter: If `collisions` is `True`, listen for collision enter events.
        :param collision_exit: If `collisions` is `True`, listen for collision exit events.
        :param collision_stay: If `collisions` is `True`, listen for collision stay events.
        :param env_collisions: If `collisions` is `True`, listen for environment collision events.
        :param occlusion: If True, add an avatar and send `Occlusion` data per frame.
        :param num_frames: Iterate for this many frames.

        :return: The frames per second (FPS).
        """

        commands = [{'$type': "load_scene",
                     'scene_name': "ProcGenScene"},
                    {"$type": "set_render_quality",
                     "render_quality": render_quality},
                    {"$type": "set_post_process",
                     "value": post_processing},
                    {"$type": "set_screen_size",
                     "width": screen_size,
                     "height": screen_size},
                    {"$type": "set_img_pass_encoding",
                     "value": png},
                    TDWUtils.create_empty_room(30, 30)]
        if boxes:
            y = 0.5
            # Create 100 boxes.
            object_ids = []
            for i in range(100):
                commands.append({"$type": "load_primitive_from_resources",
                                 "primitive_type": "Cube",
                                 "id": i,
                                 "position": {"x": 0, "y": y, "z": 0},
                                 "orientation": {"x": 0, "y": 0, "z": 0}})
                object_ids.append(i)
                y += 1.5
        transforms = "always" if transforms else "never"
        rigidbodies = "always" if rigidbodies else "never"
        bounds = "always" if bounds else "never"
        commands.extend([{"$type": "send_transforms",
                          "frequency": transforms},
                         {"$type": "send_rigidbodies",
                          "frequency": rigidbodies},
                         {"$type": "send_bounds",
                          "frequency": bounds}])
        if collisions:
            collision_types = ["obj"]
            # Listen for environment collisions, too.
            if env_collisions:
                collision_types.append("env")
            commands.append({"$type": "send_collisions",
                             "enter": collision_enter,
                             "stay": collision_stay,
                             "exit": collision_exit,
                             "collision_types": collision_types})
        if junk is not None:
            commands.append({"$type": "send_junk",
                             "frequency": "always",
                             "length": junk})
        if images or id_colors or occlusion:
            commands.extend([{"$type": "create_avatar",
                             "id": "a",
                              "type": "A_Img_Caps_Kinematic"},
                             {"$type": "teleport_avatar_to",
                              "position": {"x": 0, "y": 1.5, "z": -2}}])
        if images and pass_masks is not None:
            commands.extend([{"$type": "set_pass_masks",
                              "pass_masks": pass_masks},
                             {"$type": "send_images",
                              "frequency": "always"}])
        if id_colors:
            commands.append({"$type": "send_id_pass_segmentation_colors",
                             "frequency": "always"})
        if occlusion:
            commands.append({"$type": "send_occlusion",
                             "frequency": "always"})
        self.communicate(commands)
        frame = 0
        self.benchmark.start()
        while frame < num_frames:
            self.communicate([])
            frame += 1
        self.benchmark.stop()
        return round(self.benchmark.fps)

    def agent_benchmark(self, random_seed: int = None) -> float:
        """
        Start a performance benchmark using an embodied agent.

        :param random_seed: The random seed. If None, a random seed is randomly selected.

        :return: The frames per second (FPS).
        """

        def __get_position() -> Tuple[float, float]:
            px, pz = free_cells[free_cell_indices.pop(0)]
            return (rng.uniform(px - cell_size * 0.33, px + cell_size * 0.33),
                    rng.uniform(pz - cell_size * 0.33, pz + cell_size * 0.33))

        if random_seed is None:
            rng: np.random.RandomState = np.random.RandomState()
        else:
            rng = np.random.RandomState(random_seed)
        cell_size = 0.5
        occupancy_map = np.array([[-1, -1, -1, -1, -1, -1, -1, -1, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, 0, 0, 0, 0, 0, 0, 0, -1],
                                  [-1, -1, -1, -1, -1, -1, -1, -1, -1]])
        free_cells = []
        for ix, iz in np.ndindex(occupancy_map.shape):
            if occupancy_map[ix][iz] == 0:
                x = -2.0 + (ix * cell_size)
                z = -2.0 + (iz * cell_size)
                free_cells.append((x, z))
        free_cell_indices = list(range(len(free_cells)))
        rng.shuffle(free_cell_indices)
        free_cell_indices = list(free_cell_indices)

        commands = [{'$type': "load_scene",
                     'scene_name': "ProcGenScene"},
                    {"$type": "set_render_quality",
                     "render_quality": 0},
                    {"$type": "set_screen_size",
                     "width": 256,
                     "height": 256},
                    {"$type": "set_img_pass_encoding",
                     "value": False},
                    {"$type": "set_post_process",
                     "value": False},
                    TDWUtils.create_empty_room(5, 5)]
        # Add objects.
        for model_name in ["bastone_floor_lamp", "arturoalvarez_v_floor_lamp"]:
            for i in range(4):
                object_x, object_z = __get_position()
                commands.extend(self.get_add_physics_object(model_name=model_name,
                                                            object_id=self.get_unique_id(),
                                                            position={"x": object_x, "y": 0, "z": object_z}))
        # Add the avatar.
        avatar_x, avatar_z = __get_position()
        commands.extend([{"$type": "create_avatar",
                          "type": "A_Img_Caps",
                          "id": "a"},
                         {"$type": "teleport_avatar_to",
                          "position": {"x": avatar_x, "y": 0, "z": avatar_z}},
                         {"$type": "set_pass_masks",
                          "pass_masks": ["_img"]},
                         {"$type": "send_id_pass_segmentation_colors",
                          "frequency": "always"},
                         {"$type": "send_transforms",
                          "frequency": "always"},
                         {"$type": "send_collisions",
                          "frequency": "always"},
                         {"$type": "send_rigidbodies",
                          "frequency": "always"},
                         {"$type": "send_images",
                          "frequency": "always"}])
        # Start the benchmark.
        self.communicate(commands)
        self.benchmark.start()
        for trial_frame in range(1000):
            commands.clear()
            random_action = np.random.uniform(-200, 200, 2)
            # Actual TDW actions.
            for p_idx in range(5):
                commands.extend([{"$type": "move_avatar_forward_by",
                                 "magnitude": random_action[0]},
                                 {"$type": "rotate_avatar_by",
                                  "angle": random_action[1] * 8,
                                  "axis": "yaw"},
                                 {"$type": "step_physics",
                                  "frames": 1}])
            self.communicate(commands)
        self.benchmark.stop()
        return self.benchmark.fps

    def flex_benchmark(self) -> float:
        """
        Start a Flex performance benchmark.

        :return: The frames per second (FPS).
        """

        self.communicate([{'$type': 'load_scene',
                           'scene_name': 'ProcGenScene'},
                          {'$type': 'create_exterior_walls',
                           'walls': [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 0, 'y': 2}, {'x': 0, 'y': 3},
                                     {'x': 0, 'y': 4}, {'x': 1, 'y': 0}, {'x': 1, 'y': 4}, {'x': 2, 'y': 0},
                                     {'x': 2, 'y': 4}, {'x': 3, 'y': 0}, {'x': 3, 'y': 4}, {'x': 4, 'y': 0},
                                     {'x': 4, 'y': 1}, {'x': 4, 'y': 2}, {'x': 4, 'y': 3}, {'x': 4, 'y': 4}]},
                          {'$type': 'create_proc_gen_ceiling'},
                          {'$type': 'convexify_proc_gen_room'},
                          {'$type': 'create_avatar',
                           'id': 'a',
                           'type': 'A_Img_Caps_Kinematic'},
                          {'$type': 'teleport_avatar_to',
                           'position': {'x': -2, 'y': 1, 'z': -2}},
                          {'$type': 'set_avatar_forward',
                           'forward': {'x': 2, 'y': -1, 'z': 2}},
                          {'$type': 'send_camera_matrices',
                           'frequency': 'always'},
                          {'$type': 'send_flex_particles',
                           'frequency': 'always'},
                          {'$type': 'create_flex_container',
                           'gravity': {'x': 0, 'y': -9.81, 'z': 0},
                           'radius': 0.1875,
                           'solid_rest': 0.125,
                           'fluid_rest': 0.115,
                           'static_friction': 0.5,
                           'dynamic_friction': 0.33333333,
                           'particle_friction': 0.166666666,
                           'substep_count': 8,
                           'iteration_count': 8,
                           'collision_distance': 0.0625,
                           'damping': 0.1,
                           'planes': [{'x': 0, 'y': 1, 'z': 0, 'w': 0}, {'x': 0, 'y': -1, 'z': 0, 'w': 5},
                                      {'x': 1, 'y': 0, 'z': 0, 'w': 2.2}, {'x': -1, 'y': 0, 'z': 0, 'w': 2.2},
                                      {'x': 0, 'y': 0, 'z': 1, 'w': 2.2}, {'x': 0, 'y': 0, 'z': -1, 'w': 2.2}]},
                          {'$type': 'set_time_step',
                           'time_step': 0.05},
                          {'$type': 'set_render_quality',
                           'render_quality': 0},
                          {'$type': 'set_post_process',
                           'value': False},
                          {'$type': 'load_primitive_from_resources',
                           'id': 1,
                           'primitive_type': 'Cube',
                           'position': {'x': 0.16403958415021425, 'y': 0.5186866147245053, 'z': 0.5172312486447144},
                           'orientation': {'x': 0, 'y': 0, 'z': 0}},
                          {"$type": "rotate_object_to",
                           "id": 1,
                           "rotation": {'x': -0.3698290892432926, 'y': 0.09343813858449268, 'z': -0.2922975854616724, 'w': 0.8769594520504459}},
                          {"$type": "scale_object",
                           "id": 1,
                           "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
                          {'$type': 'set_kinematic_state',
                           'id': 1,
                           'is_kinematic': False},
                          {'$type': 'set_flex_soft_actor',
                           'id': 1,
                           'draw_particles': False,
                           'particle_spacing': 0.125,
                           'cluster_stiffness': 0.21856892364500366},
                          {'$type': 'assign_flex_container',
                           'id': 1,
                           'container_id': 0},
                          {'$type': 'set_flex_particles_mass',
                           'id': 1,
                           'mass': 15.625},
                          {'$type': 'set_color',
                           'id': 1,
                           'color': {'r': 0.36824153984054797, 'g': 0.9571551589530464, 'b': 0.14035078041264515, 'a': 1}},
                          {'$type': 'load_primitive_from_resources',
                           'id': 2,
                           'primitive_type': 'Cube',
                           'position': {'x': 0.47383635425791626, 'y': 0.35827517721218594, 'z': -0.7295636531890959},
                           'orientation': {'x': 0, 'y': 0, 'z': 0}},
                          {"$type": "rotate_object_to",
                           "id": 2,
                           "rotation": {'x': -0.26294416753798533, 'y': -0.28764056724783615, 'z': -0.32404784600690667, 'w': 0.862041914485243}},
                          {"$type": "scale_object",
                           "id": 2,
                           "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
                          {'$type': 'set_kinematic_state',
                           'id': 2,
                           'is_kinematic': False},
                          {'$type': 'set_flex_soft_actor',
                           'id': 2,
                           'draw_particles': False,
                           'particle_spacing': 0.125,
                           'cluster_stiffness': 0.22055267521432875},
                          {'$type': 'assign_flex_container',
                           'id': 2,
                           'container_id': 0},
                          {'$type': 'set_flex_particles_mass',
                           'id': 2,
                           'mass': 15.625},
                          {'$type': 'set_color',
                           'id': 2,
                           'color': {'r': 0.8700872583584364, 'g': 0.4736080452737105, 'b': 0.8009107519796442, 'a': 1}},
                          {'$type': 'load_primitive_from_resources',
                           'id': 3,
                           'primitive_type': 'Cube',
                           'position': {'x': -0.8337750147387952, 'y': 0.3888592806405162, 'z': -0.9812865902869348},
                           'orientation': {'x': 0, 'y': 0, 'z': 0}},
                          {"$type": "rotate_object_to",
                           "id": 3,
                           "rotation": {'x': 0.2648241162596214, 'y': 0.23805685090753817, 'z': 0.263751099599952, 'w': 0.896455509572624}},
                          {"$type": "scale_object",
                           "id": 3,
                           "scale_factor": {"x": 0.5, "y": 0.5, "z": 0.5}},
                          {'$type': 'set_kinematic_state',
                           'id': 3,
                           'is_kinematic': False},
                          {'$type': 'set_flex_soft_actor',
                           'id': 3,
                           'draw_particles': False,
                           'particle_spacing': 0.125,
                           'cluster_stiffness': 0.5247127393571944},
                          {'$type': 'assign_flex_container',
                           'id': 3,
                           'container_id': 0},
                          {'$type': 'set_flex_particles_mass',
                           'id': 3,
                           'mass': 15.625},
                          {'$type': 'set_color',
                           'id': 3,
                           'color': {'r': 0.5204774795512048, 'g': 0.6788795301189603, 'b': 0.7206326547259168, 'a': 1}},
                          {'$type': 'send_collisions',
                           'frequency': 'always',
                           'enter': True,
                           'exit': False,
                           'stay': False},
                          {'$type': 'send_transforms',
                           'frequency': 'always'}])
        self.benchmark.start()
        for i in range(2000):
            self.communicate([])
        self.benchmark.stop()
        return self.benchmark.fps
