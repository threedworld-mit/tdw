from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian, MaterialLibrarian, ModelRecord, MaterialRecord
from tdw.output_data import Images
from pathlib import Path
from tqdm import tqdm
import json


class _Screenshotter(Controller):
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

        super().__init__(port)

        self.load_streamed_scene(scene="empty_scene")

        self.communicate([{"$type": "simulate_physics",
                           "value": False},
                          {"$type": "set_screen_size",
                           "height": 1024,
                           "width": 1024},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_shadow_strength",
                           "strength": 1.0},
                          {"$type": "set_img_pass_encoding",
                           "value": False}])

        self.communicate(TDWUtils.create_avatar(position=self._get_avatar_position()))
        self.communicate([{"$type": "set_pass_masks",
                           "avatar_id": "a",
                           "pass_masks": ["_img"]},
                          {"$type": "send_images",
                          "frequency": "always"}])
        self._set_post_processing()

    def _get_visualizer_metadata(self):
        """
        Returns metadata that the Visualizer applications need.
        """

        raise Exception()

    def _get_librarian(self, library: str):
        """
        Returns the librarian object.

        :param library: The name of the library.
        """

        raise Exception()

    def _set_post_processing(self):
        """
        Adjust the default post-process settings.
        """

        raise Exception()

    def _get_avatar_position(self):
        """
        :return: The position of the avatar.
        """

        raise Exception()

    def _get_output_directory(self):
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

    def get_image(self, record):
        """
        Get an image of the asset corresponding to the record.

        :param record: The record.
        :return: The image and the frame.
        """

        raise Exception()

    def run(self, target: str):
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
                images, frame = self.get_image(record)
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

    def _get_output_directory(self):
        return Path.home().joinpath("TDWImages/ModelImages")

    def _get_avatar_position(self):
        return {"x": 1.57, "y": 3, "z": 3.56}

    def _set_post_processing(self):
        self.communicate([{"$type": "set_screen_space_reflections",
                           "enabled": True},
                          {"$type": "set_vignette",
                           "enabled": False},
                          {"$type": "set_focus_distance",
                           "focus_distance": 8.0}])

    def _get_librarian(self, library: str):
        return ModelLibrarian(library + ".json")

    def _get_visualizer_metadata(self):
        records = []
        for record in self._lib.records:
            if record.do_not_use:
                continue
            records.append({"name": record.name,
                            "wnid": record.wnid,
                            "wcategory": record.wcategory})
        records = {"records": records}
        return records

    def _record_is_ok(self, record) -> bool:
        return not record.do_not_use

    def get_image(self, record: ModelRecord):
        o_id = Controller.get_unique_id()
        self.communicate({"$type": "add_object",
                          "name": record.name,
                          "url": record.get_url(),
                          "scale_factor": record.scale_factor,
                          "rotation": record.canonical_rotation,
                          "id": o_id})

        s = TDWUtils.get_unit_scale(record) * 2

        # Scale the model and get an image.
        # Look at the model's centroid.
        resp = self.communicate([{"$type": "scale_object",
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
        return Images(resp[0]), resp[-1]


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

    def _set_post_processing(self):
        self.communicate([{"$type": "set_screen_space_reflections",
                           "enabled": False},
                          {"$type": "set_contrast",
                           "contrast": 0},
                          {"$type": "set_saturation",
                           "saturation": 0},
                          {"$type": "set_vignette",
                           "enabled": False},
                          {"$type": "set_focus_distance",
                           "focus_distance": 8.0}])

    def _get_output_directory(self):
        return Path.home().joinpath("TDWImages/MaterialImages")

    def _get_avatar_position(self):
        return {"x": -2.58, "y": 2.2, "z": 0}

    def _get_librarian(self, library: str):
        return MaterialLibrarian(library + ".json")

    def _get_visualizer_metadata(self):
        records = []
        for record in self._lib.records:
            records.append({"name": record.name,
                            "type": record.type})
        records = {"records": records}
        return records

    def _record_is_ok(self, record) -> bool:
        return True

    def get_image(self, record: MaterialRecord):
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
        resp = self.communicate({"$type": "do_nothing"})
        return Images(resp[0]), resp[-1]


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--type", default="models_core", choices=["models_full", "models_core", "materials"],
                        help="The type of screenshotter and the asset library.")
    parser.add_argument("--target", nargs="?", type=str, help="The name of a single record.")
    args = parser.parse_args()

    # Model Screenshotter.
    if args.type == "models_full" or args.type == "models_core":
        ModelScreenshotter(args.type).run(args.target)
    # Material Screenshotter.
    else:
        MaterialScreenshotter().run(args.target)
