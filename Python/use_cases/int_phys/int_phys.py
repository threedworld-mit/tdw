from typing import Dict, List, Tuple
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, MaterialLibrarian, SceneLibrarian
from tdw.output_data import Transforms, Rigidbodies, OutputData, SegmentationColors, Images
from tdw.tdw_utils import TDWUtils
from pathlib import Path
import json
import numpy as np
from PIL import Image
import random
from shutil import move
from distutils import dir_util


class Util:
    """
    Utility class.
    """

    _LIB_MATERIALS = MaterialLibrarian("materials_high.json")
    _LIB_MODELS = ModelLibrarian(str(Path("models.json").resolve()))

    @staticmethod
    def update_library() -> None:
        """
        Update the local records library to correct the local URLs for this machine.
        """

        for record in Util._LIB_MODELS.records:
            # This is a local asset bundle.
            if record.get_url().startswith("file:///"):
                # Update the URLs to match the local machine.
                for platform in record.urls:
                    p = Path(platform).joinpath(record.name)
                    record.urls[platform] = "file:///" + str(p.resolve()).replace('\\', '/')
                Util._LIB_MODELS.add_or_update_record(record, overwrite=True, write=False)
        Util._LIB_MODELS.write()

    @staticmethod
    def get_add_material(name: str) -> dict:
        """
        Returns a valid add_material command.

        :param name: The name of the material.
        """

        record = Util._LIB_MATERIALS.get_record(name)
        return {"$type": "add_material",
                "name": name,
                "url": record.get_url()}

    @staticmethod
    def get_add_object(name: str, object_id: int, position: Dict[str, float]) -> dict:
        """
        Returns a valid add_object command.

        :param name: The name of the model.
        :param object_id: The unique ID of the object.
        :param position: The initial position.
        """

        record = Util._LIB_MODELS.get_record(name)

        return {"$type": "add_object",
                "name": record.name,
                "url": record.get_url(),
                "scale_factor": record.scale_factor,
                "position": position,
                "category": record.wcategory,
                "id": object_id}

    @staticmethod
    def get_set_visual_material_commands(material_name: str, object_id: int, model_name: str) -> List[dict]:
        """
        Returns the commands required to set the visual material of each sub-object.

        :param material_name: The name of the material.
        :param object_id: The ID of the parent object.
        :param model_name: The name of the model.
        """

        record = Util._LIB_MODELS.get_record(model_name)

        commands = [Util.get_add_material(material_name)]
        for sub_object in record.substructure:
            for i in range(len(sub_object["materials"])):
                commands.extend([{"$type": "set_visual_material",
                                  "id": object_id,
                                  "material_name": material_name,
                                  "object_name": sub_object["name"],
                                  "material_index": i}])
        return commands


class State:
    """
    The current state of the scene.
    """

    def __init__(self,
                 segmentation_colors: Dict[int, Tuple[float, float, float]],
                 positions: Dict[int, Tuple[float, float, float]],
                 frame: int):
        """
        :param segmentation_colors: All segmentation colors in the camera frame, mapped to object IDs.
        :param positions: The position of each MovingObject, mapped to their ID.
        :param frame: The frame number.
        """

        self.segmentation_colors = segmentation_colors
        self.positions = positions
        self.frame = frame


class Possibility:
    """
    A Possibility is the behavior that an object might have given the scene state.
    By default, an object will just respond to the physics engine, and have no additional behavior.
    """

    def __init__(self):
        self.object_id = -1

    def get_frame_commands(self, state: State) -> List[dict]:
        """
        Returns a list of commands for this object that will be sent per frame.

        :param state: The current scene state.
        """

        return []

    def _is_occluded(self, state: State) -> bool:
        """
        Returns true if this object is hidden by an occluder.
        :param state: The current trial state.
        """

        return self.object_id not in state.segmentation_colors


class Hideable(Possibility):
    """
    If an object is Hideable, then it will be hidden when it goes behind a collider.
    """

    def __init__(self):
        self.hidden = False

        super().__init__()

    def get_frame_commands(self, state: State) -> List[dict]:
        # If this object is occluded by a wall and isn't already hidden, maybe hide it.
        if not self.hidden and self._is_occluded(state) and state.positions[self.object_id][0] <= 1:
            self.hidden = True
            return [{"$type": "hide_object",
                     "id": self.object_id}]
        else:
            return []


class Teleportable(Possibility):
    """
    Randomly teleport an object at a given frame.
    """

    def __init__(self, frame: int, radius: float = 1.5):
        self.frame = frame
        self.radius = radius

        super().__init__()

    def get_frame_commands(self, state: State) -> List[dict]:
        if state.frame == self.frame:
            pos_0 = np.array(state.positions[self.object_id])
            pos_1 = TDWUtils.get_random_point_in_circle(pos_0, self.radius)
            return [{"$type": "teleport_object",
                     "position": {"x": pos_0[0], "y": pos_1[1], "z": pos_0[2]},
                     "id": self.object_id}]
        else:
            return []


class Dragger(Possibility):
    """
    Slow down an occluded object.
    """

    def __init__(self, drag: float = 200):
        self.dragged = False
        self.drag = drag
        super().__init__()

    def get_frame_commands(self, state: State) -> List[dict]:
        if not self.dragged and self._is_occluded(state):
            self.dragged = True
            return [{"$type": "set_object_drag",
                     "id": self.object_id,
                     "drag": self.drag,
                     "angular_drag": 0.05}]
        else:
            return []


class TDWObject:
    def __init__(self,
                 model_name: str,
                 initial_position: Dict[str, float]):
        """
        :param model_name: The name of the 3D model in the model library.
        :param initial_position: The initial position of the object.
        """

        self.object_id = Controller.get_unique_id()
        self.initial_position = initial_position
        self.model_name = model_name

    def get_init_commands(self) -> List[dict]:
        return [Util.get_add_object(self.model_name, self.object_id, self.initial_position)]

    def get_frame_commands(self, state: State) -> List[dict]:
        """
        Returns a list of commands for this object that will be sent per frame.

        :param state: The current scene state.
        """

        raise Exception()


class Occluder(TDWObject):
    """
    An occluder is a slab that can hide moving objects.
    """

    def __init__(self, x: float):
        """
        :param x: The x positional coordinate.
        """

        self.theta = 0
        self.delta_theta = -1

        super().__init__(model_name="occluder", initial_position={"x": x, "y": 0, "z": 0})

    def get_init_commands(self) -> List[dict]:
        commands = super().get_init_commands()

        # Start the walls facing the ground.
        # Disable physics.
        # Give the walls nice-looking materials.
        commands.extend([{"$type": "rotate_object_by",
                          "angle": 90,
                          "id": self.object_id,
                          "axis": "pitch"},
                         {"$type": "set_kinematic_state",
                          "id": self.object_id,
                          "is_kinematic": True,
                          "use_gravity": False}])
        commands.extend(Util.get_set_visual_material_commands("marble_white", self.object_id, self.model_name))

        return commands

    def get_frame_commands(self, state: State) -> List[dict]:
        # Rotate the object per frame.
        commands = [{"$type": "rotate_object_by",
                     "angle": self.delta_theta,
                     "id": self.object_id,
                     "axis": "pitch"}]
        self.theta += self.delta_theta
        if (self.delta_theta < 0 and self.theta <= -90) or (self.delta_theta > 0 and self.theta > 0):
            self.delta_theta *= -1
        return commands


class MovingObject(TDWObject):
    """
    A moving object can have possible or impossible behavior.
    """

    def __init__(self,
                 model_name: str,
                 initial_position: Dict[str, float],
                 material: str,
                 possibility: Possibility):
        """
        :param possibility: Possible/impossible behavior.
        :param material: The name of the material.
        """

        self.possibility = possibility
        self.material = material
        super().__init__(model_name=model_name, initial_position=initial_position)

    def get_frame_commands(self, state: State) -> List[dict]:
        return self.possibility.get_frame_commands(state)


class StaticObject(MovingObject):
    """
    An object that doesn't move.
    """

    def get_init_commands(self) -> List[dict]:
        commands = super().get_init_commands()

        # Disable physics and set the visual material.
        commands.extend([{"$type": "set_kinematic_state",
                          "id": self.object_id,
                          "is_kinematic": True,
                          "use_gravity": False}])
        commands.extend(Util.get_set_visual_material_commands(self.material, self.object_id, self.model_name))
        return commands


class SimpleBall(MovingObject):
    """
    A ball that moves linearly on the ground.
    """
    Z = -0.5

    def __init__(self,
                 x: float,
                 material: str,
                 speed: float,
                 possibility: Possibility):
        """
        :param speed: The speed of the object.
        :param possibility: The possibility logic.
        """

        self.x = x
        self.speed = speed

        super().__init__(model_name="sphere", initial_position={"x": x, "y": 0, "z": SimpleBall.Z},
                         possibility=possibility, material=material)

    def get_init_commands(self) -> List[dict]:
        commands = super().get_init_commands()

        # Disable physics and set the visual material.
        commands.extend([{"$type": "set_kinematic_state",
                          "id": self.object_id,
                          "is_kinematic": True,
                          "use_gravity": False}])
        commands.extend(Util.get_set_visual_material_commands(self.material, self.object_id, self.model_name))
        return commands

    def get_frame_commands(self, state: State) -> List[dict]:
        commands = [{"$type": "teleport_object",
                     "position": {"x": self.x, "y": 0, "z": SimpleBall.Z},
                     "id": self.object_id}]
        self.x += self.speed
        commands.extend(self.possibility.get_frame_commands(state))
        return commands


class ShapeTransform(Possibility):
    """
    Transform the object into a difference shape.
    """
    def __init__(self, new_shape: str, obj: MovingObject):
        self.transformed = False
        self.obj = obj
        self.new_shape = new_shape

        super().__init__()

    def get_frame_commands(self, state: State) -> List[dict]:
        if not self.transformed and self._is_occluded(state):
            self.transformed = True
            commands = [{"$type": "destroy_object",
                         "id": self.object_id},
                        Util.get_add_object(self.new_shape, self.object_id, self.obj.initial_position),
                        {"$type": "set_kinematic_state",
                         "id": self.object_id,
                         "is_kinematic": True,
                         "use_gravity": False}]
            commands.extend(Util.get_set_visual_material_commands(self.obj.material, self.object_id, self.new_shape))
            return commands
        else:
            return []


class PhysicsObject(MovingObject):
    def __init__(self,
                 model_name: str,
                 initial_position: Dict[str, float],
                 possibility: Possibility,
                 dynamic_friction: float,
                 static_friction: float,
                 bounciness: float,
                 mass: float,
                 look_at=TDWUtils.VECTOR3_ZERO,
                 force=5):

        super().__init__(model_name=model_name, initial_position=initial_position,
                         possibility=possibility, material="")
        self.dynamic_friction = dynamic_friction
        self.static_friction = static_friction
        self.bounciness = bounciness
        self.mass = mass
        self.look_at = look_at
        self.force = force

    def get_init_commands(self) -> List[dict]:
        commands = super().get_init_commands()
        commands.extend([{"$type": "set_mass",
                          "mass": self.mass,
                          "id": self.object_id},
                         {"$type": "scale_object",
                          "scale_factor": {"x": 1.5, "y": 1.5, "z": 1.5},
                          "id": self.object_id},
                         {"$type": "set_physic_material",
                          "dynamic_friction": self.dynamic_friction,
                          "static_friction": self.static_friction,
                          "bounciness": self.bounciness,
                          "id": self.object_id},
                         {"$type": "object_look_at_position",
                          "position": self.look_at,
                          "id": self.object_id},
                         {"$type": "apply_force_magnitude_to_object",
                          "magnitude": self.force,
                          "id": self.object_id}])
        return commands

    def get_frame_commands(self, state: State) -> List[dict]:
        return self.possibility.get_frame_commands(state)


class Trial:
    """
    Logic for a single trial that can be "plugged into" a controller.
    """

    ROOT_DIR = Path.home().joinpath("int_phys_output")

    def __init__(self, occluders: List[Occluder], moving_objects: List[MovingObject], scene_commands: List[dict],
                 output_dir: str, num_frames: int = 180):
        """
        :param occluders: The occluders in this trial.
        :param moving_objects: The moving objects in this trial.
        :param scene_commands: The commands used to initialize the scene for the trial.
        :param output_dir: The output data directory.
        :param num_frames: The trial will run for this many frames.
        """

        avatar_z = 8

        self.occluders = occluders
        self.moving_objects = moving_objects
        self.init_commands = scene_commands[:]

        # Store the object ID for the Possibility object.
        for i in range(len(self.moving_objects)):
            self.moving_objects[i].possibility.object_id = self.moving_objects[i].object_id

        # Set the screen size and rendering quality.
        self.init_commands.extend([{"$type": "set_screen_size",
                                    "width": 512,
                                    "height": 512},
                                   {"$type": "set_render_quality",
                                    "render_quality": 5}])
        # Initialize the objects.
        for o in self.occluders:
            self.init_commands.extend(o.get_init_commands())
        for m in self.moving_objects:
            self.init_commands.extend(m.get_init_commands())
        # Initialize the avatar.
        self.init_commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1.5, "z": avatar_z},
                                                         look_at={"x": 0, "y": 1.5, "z": 0}))
        self.m_ids = [obj.object_id for obj in moving_objects]

        # Set the pass masks.
        # Set post-process values.
        # Request segmentation colors.
        self.init_commands.extend([{"$type": "set_pass_masks",
                                   "pass_masks": ["_img", "_id", "_depth"]},
                                   {"$type": "set_focus_distance",
                                    "focus_distance": avatar_z + 0.5},
                                   {"$type": "set_vignette",
                                    "enabled": False},
                                   {"$type": "send_segmentation_colors",
                                    "ids": self.m_ids,
                                    "frequency": "once"}])

        self.output_dir = Trial.ROOT_DIR.joinpath(output_dir)
        self.num_frames = num_frames

        if not self.output_dir:
            self.output_dir.mkdir(parents=True)
        self.output_dir = str(Path.resolve(self.output_dir))

    def run(self, c: Controller):
        """
        Run the trial and save the output.

        :param c: The controller.
        """

        print(f"Images will be saved to: {self.output_dir}")

        # Initialize the scene.
        resp = c.communicate(self.init_commands)
        # Get a map of the segmentation colors.
        segm = SegmentationColors(resp[0])
        for i in range(segm.get_num()):
            for obj in self.moving_objects:
                if obj.object_id == segm.get_object_id(i):
                    obj.possibility.segmentation_color = segm.get_object_color(i)

        # Request scene data and images per frame.
        frame_data: List[dict] = []
        resp = c.communicate([{"$type": "send_images",
                               "frequency": "always"},
                              {"$type": "send_transforms",
                               "ids": self.m_ids,
                               "frequency": "always"},
                              {"$type": "send_rigidbodies",
                               "ids": self.m_ids,
                               "frequency": "always"}])

        # Run the trial.
        for frame in range(self.num_frames):
            colors: Dict[int, Tuple[int, int, int]] = {}
            transforms: Dict[int, Tuple[float, float, float]] = {}

            transform_data = None
            rigidbody_data = None

            # Parse the output data.
            for r in resp[:-1]:
                r_id = OutputData.get_data_type_id(r)
                # Record all Transforms data.
                if r_id == "tran":
                    transform_data = Transforms(r)
                    for i in range(transform_data.get_num()):
                        transforms.update({transform_data.get_id(i): transform_data.get_position(i)})
                # Record all Rigidbodies data.
                elif r_id == "rigi":
                    rigidbody_data = Rigidbodies(r)
                # Save the images.
                elif r_id == "imag":
                    images = Images(r)
                    for p in range(images.get_num_passes()):
                        if images.get_pass_mask(p) == "_id":
                            image_colors = TDWUtils.get_pil_image(images, p).getcolors()
                            for ic in image_colors:
                                color = ic[1]
                                for obj in self.moving_objects:
                                    if obj.possibility.segmentation_color == color:
                                        colors.update({obj.object_id: color})

                    TDWUtils.save_images(Images(r), TDWUtils.zero_padding(frame), output_directory=self.output_dir)

            # Append frame data.
            frame_data.append(Trial._get_frame_state(transform_data, rigidbody_data, frame))

            # Build the frame state.
            state = State(colors, transforms, frame)

            # Apply object actions.
            commands = []
            for o in self.occluders:
                commands.extend(o.get_frame_commands(state))
            for mo in self.moving_objects:
                commands.extend(mo.get_frame_commands(state))
            if len(commands) == 0:
                commands = [{"$type": "do_nothing"}]

            # Send the commands and update the state.
            resp = c.communicate(commands)

        # Cleanup.
        c.communicate([{"$type": "destroy_all_objects"},
                       {"$type": "unload_asset_bundles"},
                       {"$type": "send_images",
                        "frequency": "never"},
                       {"$type": "send_transforms",
                        "ids": self.m_ids,
                        "frequency": "never"},
                       {"$type": "send_rigidbodies",
                        "ids": self.m_ids,
                        "frequency": "never"}])

        print("\tGenerated images.")
        # Output the scene metadata.
        Path(self.output_dir).joinpath("state.json").write_text(json.dumps({"frames": frame_data}), encoding="utf-8")
        print("\tWrote state file.")

        # Get _id passes with randomized colors.
        self._randomize_segmentation_colors()
        print("\tCreated random segmentation colors.")

        # Organize the images.
        self._organize_output()
        print("\tOrganized files")

    @staticmethod
    def _get_frame_state(t: Transforms, r: Rigidbodies, num: int) -> dict:
        """
        Returns a dictionary representing the current frame state.

        :param t: The transforms data.
        :param r: The rigidbodies data.
        :param num: The current frame.
        """

        objects = dict()
        assert t.get_num() == r.get_num()
        for i in range(t.get_num()):
            objects.update({t.get_id(i): {"position": t.get_position(i),
                                          "rotation": t.get_rotation(i),
                                          "forward": t.get_forward(i),
                                          "velocity": r.get_velocity(i),
                                          "angular_velocity": r.get_angular_velocity(i),
                                          "mass": r.get_mass(i)}})
        return {"frame": num, "objects": objects}

    def _randomize_segmentation_colors(self) -> None:
        """
        Randomize all segmentation colors in the images.
        """

        black = np.array([0, 0, 0])

        root_dir = Path(self.output_dir)
        # Randomize each segmentation color per frame.
        for f in root_dir.glob("id_*.png"):
            frame = np.array(Image.open(str(f.resolve())))
            unique = np.unique(frame.reshape(-1, frame.shape[2]), axis=0)
            unique = np.delete(unique, black, axis=0)
            replace = unique.copy()
            for i in range(len(replace)):
                replace[i] = np.array((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            for i in range(len(unique)):
                frame = np.where(frame == unique[i], replace[i], frame)
            im = Image.fromarray(frame)

            # Save a copy of the image.
            image_path = str(root_dir.joinpath("id_random_" + f.stem.split("_")[1] + ".png").resolve())
            im.save(image_path)

    def _organize_output(self) -> None:
        """
        Organize each type of image into a separate sub-directory.
        """

        root_dir = Path(self.output_dir)

        for sub_dir in ["img", "id_random", "depth", "id"]:
            sd = root_dir.joinpath(sub_dir)
            sd.mkdir()
            for f in root_dir.glob(f"{sub_dir}_*.png"):
                dest = sd.joinpath(f.name)
                move(str(f.resolve()), str(dest.resolve()))


if __name__ == "__main__":
    # Remove old data.
    if Trial.ROOT_DIR.exists():
        dir_util.remove_tree(str(Trial.ROOT_DIR.resolve()))

    Util.update_library()

    # Object Permanence - Possible
    occ_opp: List[Occluder] = [Occluder(-1.5), Occluder(1.5)]
    mov_opp: List[MovingObject] = [SimpleBall(-8, material="bronze_yellow", possibility=Possibility(), speed=0.1)]
    sce_opp: List[dict] = [{"$type": "load_scene", "scene_name": "ProcGenScene"},
                           TDWUtils.create_empty_room(25, 25),
                           Util.get_add_material("parquet_long_horizontal_clean"),
                           {"$type": "set_proc_gen_floor_material",
                            "name": "parquet_long_horizontal_clean"},
                           {"$type": "set_proc_gen_floor_texture_scale",
                            "scale": {"x": 8, "y": 8}}]
    opp = Trial(occ_opp, mov_opp, sce_opp, "opp")

    # Object Permanence - Impossible
    occ_opi: List[Occluder] = [Occluder(-1.5), Occluder(1.5)]
    mov_opi = [SimpleBall(-8, material="bronze_yellow", possibility=Possibility(), speed=0.1),
               SimpleBall(8, material="aluminium_foil", possibility=Hideable(), speed=-0.1)]
    sce_opi = sce_opp
    opi = Trial(occ_opi, mov_opi, sce_opi, "opi")

    # Shape Constancy - Possible
    occ_shp: List[Occluder] = [Occluder(1.5)]
    mov_shp = [StaticObject(model_name="sphere", initial_position={"x": -1.5, "y": 0, "z": -0.5},
                            material="aluminium_foil", possibility=Possibility()),
               StaticObject(model_name="cube", initial_position={"x": 0, "y": 0, "z": -0.5},
                            material="bronze_yellow", possibility=Possibility()),
               StaticObject(model_name="sphere", initial_position={"x": 1.5, "y": 0, "z": -0.5},
                            material="aluminium_foil", possibility=Possibility())]
    sce_shp: List[dict] = [{"$type": "load_scene", "scene_name": "ProcGenScene"},
                           TDWUtils.create_empty_room(25, 25),
                           Util.get_add_material("concrete_01"),
                           {"$type": "set_proc_gen_floor_material",
                            "name": "concrete_01"},
                           {"$type": "set_proc_gen_floor_texture_scale",
                            "scale": {"x": 8, "y": 8}}]
    shp = Trial(occ_shp, mov_shp, sce_shp, "scp")

    # Shape Constancy - Impossible
    occ_shi: List[Occluder] = [Occluder(1.5)]
    m = StaticObject(model_name="sphere", initial_position={"x": 1.5, "y": 0, "z": -0.5},
                     material="aluminium_foil", possibility=Possibility())
    m.possibility = ShapeTransform("cone", m)
    mov_shi = [m,
               StaticObject(model_name="cube", initial_position={"x": 0, "y": 0, "z": -0.5},
                            material="bronze_yellow", possibility=Possibility()),
               StaticObject(model_name="sphere", initial_position={"x": -1.5, "y": 0, "z": -0.5},
                            material="aluminium_foil", possibility=Possibility())]
    sce_shi = sce_shp
    shi = Trial(occ_shi, mov_shi, sce_shi, "sci")

    # Spatio-Temporal Continuity - Possible
    occ_stp: List[Occluder] = []
    mov_stp = [PhysicsObject(model_name="chair_eames_plastic_armchair", initial_position={"x": 3, "y": 2, "z": 0.5},
                             possibility=Possibility(),
                             dynamic_friction=0.2, static_friction=0.2, bounciness=0.9, mass=5),
               PhysicsObject(model_name="duffle_bag", initial_position={"x": -3, "y": 2, "z": 0.5},
                             possibility=Possibility(),
                             dynamic_friction=0.5, static_friction=0.6, bounciness=0.9, mass=8)]
    lib_scenes = SceneLibrarian()
    record_scene = lib_scenes.get_record("building_site")
    sce_stp = [{"$type": "add_scene",
                "name": record_scene.name,
                "url": record_scene.get_url()}]
    stp = Trial(occ_stp, mov_stp, sce_stp, "stp")

    # Spatio-Temporal Continuity - Impossible
    occ_sti = occ_stp
    mov_sti = [PhysicsObject(model_name="chair_eames_plastic_armchair", initial_position={"x": 3, "y": 2, "z": 0.5},
                             possibility=Teleportable(60),
                             dynamic_friction=0.2, static_friction=0.2, bounciness=0.9, mass=5),
               PhysicsObject(model_name="duffle_bag", initial_position={"x": -3, "y": 2, "z": 0.5},
                             possibility=Possibility(),
                             dynamic_friction=0.5, static_friction=0.6, bounciness=0.9, mass=8)]
    sce_sti = sce_stp
    sti = Trial(occ_sti, mov_sti, sce_sti, "sti")

    # Energy Conversation - Possible
    occ_ecp: List[Occluder] = [Occluder(0)]
    mov_ecp: List[MovingObject] = [SimpleBall(x=-8, speed=0.1, material="aluminium_foil", possibility=Possibility()),
                                   PhysicsObject(model_name="chair_eames_plastic_armchair",
                                                 initial_position={"x": 1, "y": 3, "z": -1.5},
                                                 possibility=Possibility(),
                                                 dynamic_friction=0.2, static_friction=0.2, bounciness=0.9, mass=5)]
    sce_ecp = sce_stp
    ecp = Trial(occ_ecp, mov_ecp, sce_ecp, "ecp")

    # Energy Conservation - Impossible
    occ_eci: List[Occluder] = [Occluder(0)]
    mov_eci: List[MovingObject] = [SimpleBall(x=-8, speed=0.1, material="aluminium_foil", possibility=Possibility()),
                                   PhysicsObject(model_name="chair_eames_plastic_armchair",
                                                 initial_position={"x": 1, "y": 3, "z": -1.5},
                                                 possibility=Dragger(),
                                                 dynamic_friction=0.2, static_friction=0.2, bounciness=0.9, mass=5)]
    sce_eci = sce_stp
    eci = Trial(occ_eci, mov_eci, sce_eci, "eci")

    # Run the trials.
    c = Controller()
    for trial in [opp, opi, shp, shi, stp, sti, ecp, eci]:
        trial.run(c)
    # End the simulation.
    c.communicate({"$type": "terminate"})
