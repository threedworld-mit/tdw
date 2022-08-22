from pathlib import Path
from json import loads
from typing import List, Tuple
from pkg_resources import resource_filename
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.container_manager import ContainerManager
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial


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
            collision_stay: bool = True, env_collisions: bool = True, occlusion: bool = False, obi: bool = False,
            obi_particle_data: bool = False, num_frames: int = 5000) -> float:
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
        :param obi: If True, add Obi colliders and collision materials to each object.
        :param obi_particle_data: If True, send `ObiParticles` per frame. Ignored if `obi` is `False`.
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
            # Initialize for Obi.
            if obi:
                obi_collision_material = CollisionMaterial()
                commands.extend([{"$type": "destroy_obi_solver"},
                                 {"$type": "create_obi_solver"},
                                 {"$type": "create_floor_obi_colliders"}])
                floor_material_command = {"$type": "set_floor_obi_collision_material"}
                floor_material_command.update(obi_collision_material.to_dict())
                commands.append(floor_material_command)
                for object_id in object_ids:
                    commands.append({"$type": "create_obi_colliders",
                                     "id": object_id})
                    object_material_command = {"$type": "set_obi_collision_material",
                                               "id": object_id}
                    object_material_command.update(obi_collision_material.to_dict())
                    commands.append(object_material_command)
                if obi_particle_data:
                    commands.append({"$type": "send_obi_particles",
                                     "frequency": "always"})
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

    def kitchen_benchmark(self) -> float:
        """
        Load a pre-generated proc-gen kitchen, request object output data, and return the speed.

        :return: The frames per second (FPS).
        """

        # Initialize the add-ons.
        self.add_ons = [ObjectManager(transforms=True, rigidbodies=False, bounds=False),
                        ContainerManager(),
                        CompositeObjectManager(),
                        self.benchmark]
        # Create the scene.
        self.communicate(loads(Path(resource_filename(__name__, "kitchen_commands.json")).read_text()))
        self.benchmark.start()
        for i in range(2000):
            self.communicate([])
        self.benchmark.stop()
        # Clear the add-ons.
        self.add_ons = [self.benchmark]
        return self.benchmark.fps
