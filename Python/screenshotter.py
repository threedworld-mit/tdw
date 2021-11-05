from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path
import json
from tqdm import tqdm
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import _Librarian, ModelLibrarian, MaterialLibrarian, ModelRecord, MaterialRecord
from tdw.output_data import Images


class _Screenshotter(Controller, ABC):
    """
    Base class for screenshotter controllers.
    """

    def __init__(self, library: str, port=1071):
        self._lib = self._get_librarian(library)
        output_dir = self._get_output_directory()
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        self.output_dir = str(output_dir.resolve())
        Path(self.output_dir).joinpath("records.json").write_text(
            json.dumps(self._get_visualizer_metadata()), encoding="utf-8")

        super().__init__(port, launch_build=False)

        commands = [self.get_add_scene(scene_name="empty_scene"),
                    {"$type": "simulate_physics",
                     "value": False},
                    {"$type": "set_screen_size",
                     "height": 1024,
                     "width": 1024},
                    {"$type": "set_render_quality",
                     "render_quality": 5},
                    {"$type": "set_shadow_strength",
                     "strength": 1.0},
                    {"$type": "set_img_pass_encoding",
                     "value": False}]
        commands.extend(TDWUtils.create_avatar(position=self._get_avatar_position()))
        commands.extend([{"$type": "set_pass_masks",
                          "pass_masks": ["_img"]},
                         {"$type": "send_images",
                          "frequency": "always"}])
        commands.extend(self._get_post_processing_commands())
        self.communicate(commands)

    @abstractmethod
    def _get_visualizer_metadata(self) -> List[dict]:
        """
        Returns metadata that the Visualizer applications need.
        """

        raise Exception()

    @abstractmethod
    def _get_librarian(self, library: str) -> _Librarian:
        """
        Returns the librarian object.

        :param library: The name of the library.
        """

        raise Exception()

    @abstractmethod
    def _get_post_processing_commands(self) -> List[dict]:
        """
        :return: A list of commands for adjusting the post-processing settings.
        """

        raise Exception()

    @abstractmethod
    def _get_avatar_position(self) -> Dict[str, float]:
        """
        :return: The position of the avatar.
        """

        raise Exception()

    def _get_output_directory(self) -> Path:
        """
        :return: The output directory for the images.
        """

        raise Exception()

    def _record_is_ok(self, record) -> bool:
        """
        Returns true if this is a valid record.

        :param record: The record.
        """

        raise Exception()

    def get_image(self, record) -> Images:
        """
        Get an image of the asset corresponding to the record.

        :param record: The record.

        :return: The image output data.
        """

        raise Exception()

    def run(self, target: str) -> None:
        """
        Take a screenshot per record.

        :param target: The target model. If none, target all models.
        """

        # Get an image of just one model.
        if args.target:
            records = [self._lib.get_record(target)]
        # Get an image of all models.
        else:
            records = self._lib.records

        pbar = tqdm(total=len(records))
        for record in records:
            if not self._record_is_ok(record):
                pbar.update(1)
                continue
            record_name = record.name

            # Skip an image that exists.
            if not Path(self.output_dir).joinpath(record_name + ".jpg").exists():
                # Capture a screenshot.
                images = self.get_image(record)
                # Save the image.
                TDWUtils.save_images(images, record_name,
                                     output_directory=self.output_dir, append_pass=False)
            pbar.update(1)
        # Terminate the build.
        self.communicate({"$type": "terminate"})
        pbar.close()


class ModelScreenshotter(_Screenshotter):
    """
    Create images of every model in the model library, or of a specified model.
    """

    def __init__(self, temp_urls: bool, library: str, port=1071):
        super().__init__(library=library, port=port)
        if temp_urls:
            self.communicate({"$type": "use_pre_signed_urls",
                              "value": False})

    def _get_output_directory(self) -> Path:
        return Path.home().joinpath("TDWImages/ModelImages")

    def _get_avatar_position(self) -> Dict[str, float]:
        return {"x": 1.57, "y": 3, "z": 3.56}

    def _get_post_processing_commands(self) -> List[dict]:
        return [{"$type": "set_screen_space_reflections",
                 "enabled": True},
                {"$type": "set_vignette",
                 "enabled": False},
                {"$type": "set_focus_distance",
                 "focus_distance": 8.0}]

    def _get_librarian(self, library: str) -> ModelLibrarian:
        return ModelLibrarian(library + ".json")

    def _get_visualizer_metadata(self) -> List[dict]:
        self._lib: ModelLibrarian
        records: List[dict] = []
        for record in self._lib.records:
            if record.do_not_use:
                continue
            records.append({"name": record.name,
                            "wnid": record.wnid,
                            "wcategory": record.wcategory})
        return records

    def _record_is_ok(self, record) -> bool:
        return not record.do_not_use

    def get_image(self, record: ModelRecord) -> Images:
        o_id = Controller.get_unique_id()
        s = TDWUtils.get_unit_scale(record) * 2
        # Add the model.
        # Scale the model and get an image.
        # Look at the model's centroid.
        resp = self.communicate([{"$type": "add_object",
                                  "name": record.name,
                                  "url": record.get_url(),
                                  "scale_factor": record.scale_factor,
                                  "rotation": record.canonical_rotation,
                                  "id": o_id},
                                 {"$type": "scale_object",
                                  "id": o_id,
                                  "scale_factor": {"x": s, "y": s, "z": s}},
                                 {"$type": "look_at",
                                  "avatar_id": "a",
                                  "object_id": o_id,
                                  "use_centroid": True}])
        # Destroy the model and unload the asset bundle.
        self.communicate([{"$type": "destroy_object",
                          "id": o_id},
                          {"$type": "unload_asset_bundles"}])
        return Images(resp[0])


class MaterialScreenshotter(_Screenshotter):
    """
    Create images of every material in the material library, or of a specified material.
    """

    def __init__(self, port=1071):
        super().__init__(library="materials_high", port=port)

        # Add a sphere and a cube. Materials will be added to these objects.
        # Push cube back in the frame slightly, so it looks like its the same size (purely aesthetic).
        # Set the avatar to look at the point between the two objects.
        self.sphere_id = self.get_unique_id()
        self.cube_id = self.get_unique_id()
        self.communicate([{"$type": "load_primitive_from_resources",
                           "id": self.sphere_id,
                           "primitive_type": "Sphere",
                           "position": {"x": 0, "y": 0.5, "z": 0.75}},
                          {"$type": "load_primitive_from_resources",
                           "id": self.cube_id,
                           "primitive_type": "Cube",
                           "position": {"x": 0.5, "y": 0.5, "z": -0.75},
                           "orientation": {"x": 0, "y": -15, "z": 0}},
                          {"$type": "look_at_position",
                           "avatar_id": "a",
                           "position": {"x": 0, "y": 0.5, "z": 0}},
                          {"$type": "rotate_sensor_container_by",
                           "angle": 5,
                           "avatar_id": "a",
                           "axis": "pitch"}])

    def _get_post_processing_commands(self) -> List[dict]:
        return [{"$type": "set_screen_space_reflections",
                 "enabled": False},
                {"$type": "set_contrast",
                 "contrast": 0},
                {"$type": "set_saturation",
                 "saturation": 0},
                {"$type": "set_vignette",
                 "enabled": False},
                {"$type": "set_focus_distance",
                 "focus_distance": 8.0}]

    def _get_output_directory(self) -> Path:
        return Path.home().joinpath("TDWImages/MaterialImages")

    def _get_avatar_position(self) -> Dict[str, float]:
        return {"x": -2.58, "y": 2.2, "z": 0}

    def _get_librarian(self, library: str) -> MaterialLibrarian:
        return MaterialLibrarian(library + ".json")

    def _get_visualizer_metadata(self) -> List[dict]:
        records = []
        self._lib: MaterialLibrarian
        for record in self._lib.records:
            records.append({"name": record.name,
                            "type": record.type})
        return records

    def _record_is_ok(self, record) -> bool:
        return True

    def get_image(self, record: MaterialRecord) -> Images:
        self.communicate([self.get_add_material(record.name),
                          {"$type": "set_primitive_visual_material",
                           "id": self.sphere_id,
                           "name": record.name,
                           "quality": "high"},
                          {"$type": "set_primitive_visual_material",
                           "id": self.cube_id,
                           "name": record.name,
                           "quality": "high"}])
        # Capture the image the following frame to allow it to initialize correctly.
        resp = self.communicate([])
        return Images(resp[0])


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--type", default="models_core", choices=["models_full", "models_core", "materials"],
                        help="The type of screenshotter and the asset library.")
    parser.add_argument("--target", nargs="?", type=str, help="The name of a single record.")
    parser.add_argument("--temp_urls", action="store_true",
                        help="Use temporary pre-signed URLs. Only include this argument if `--type models_full` and"
                             " you're experiencing segfaults on Linux when downloading models.")
    args = parser.parse_args()

    # Model Screenshotter.
    if args.type == "models_full" or args.type == "models_core":
        ModelScreenshotter((True if args.temp_urls is not None else False), args.type).run(args.target)
    # Material Screenshotter.
    else:
        MaterialScreenshotter().run(args.target)
