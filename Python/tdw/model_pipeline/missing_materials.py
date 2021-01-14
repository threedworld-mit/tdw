from tdw.controller import Controller
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.output_data import Images
from tdw.backend.paths import ASSET_BUNDLE_VERIFIER_OUTPUT_DIR
from PIL import Image
from io import BytesIO
from tdw.tdw_utils import TDWUtils
from math import radians, sin, cos
from tqdm import tqdm
import io


class MissingMaterials:
    """
    Check for missing materials.
    """

    HELL_PINK = (255, 0, 255)
    DELTA_THETA = 15
    OUTPUT_FILE = ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.joinpath("missing_materials.txt")
    if not ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.exists():
        ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.mkdir(parents=True)
    OBJECT_ID = 0

    @staticmethod
    def start(c: Controller) -> None:
        """
        Start the controller.

        :param c: The controller.
        """

        print(f"Results will be saved to: {MissingMaterials.OUTPUT_FILE}")

        c.start()

        c.communicate([{"$type": "simulate_physics",
                        "value": False},
                       {"$type": "create_empty_environment"},
                       {"$type": "set_render_quality",
                        "render_quality": 0},
                       {"$type": "set_post_process",
                        "value": False},
                       {"$type": "create_avatar",
                        "id": "a",
                        "type": "A_Img_Caps_Kinematic"},
                       {"$type": "set_pass_masks",
                        "pass_masks": ["_img"]}])

    @staticmethod
    def materials_are_missing(c: Controller, record: ModelRecord, url: str) -> bool:
        """
        Check for missing materials.

        :param c: The controller.
        :param record: The model metadata record.
        :param url: The path to the model.

        :return: True if the model is missing materials.
        """

        # Disable post-processing.
        # Disable shadows.
        # Create the avatar.
        # Set pass masks.
        # Send images.
        # Add the object.
        # Add the object.
        # Load the bounds of the model.
        scale = TDWUtils.get_unit_scale(record)
        c.communicate([{"$type": "send_images",
                        "frequency": "always"},
                       {"$type": "add_object",
                        "name": record.name,
                        "url": url,
                        "scale_factor": record.scale_factor,
                        "id": MissingMaterials.OBJECT_ID},
                       {"$type": "scale_object",
                        "id": MissingMaterials.OBJECT_ID,
                        "scale_factor": {"x": scale, "y": scale, "z": scale}}])
        x = 1.75
        y = 0.5
        z = 0

        # Equatorial orbit.
        theta = 0
        while theta < 360:
            # Get the new position.
            rad = radians(theta)
            x1 = cos(rad) * x - sin(rad) * z
            z1 = sin(rad) * x + cos(rad) * z

            if MissingMaterials._orbit_and_capture_image(c, x1, y, z1):
                return True
            theta += MissingMaterials.DELTA_THETA

        # Polar orbit.
        theta = 0
        while theta < 360:
            # Get the new position.
            rad = radians(theta)
            x1 = cos(rad) * x - sin(rad) * z
            y1 = (sin(rad) * x + cos(rad) * z) + y

            if MissingMaterials._orbit_and_capture_image(c, x1, y1, z):
                return True
            theta += MissingMaterials.DELTA_THETA

        return False

    @staticmethod
    def _orbit_and_capture_image(c: Controller, x: float, y: float, z: float) -> bool:
        """
        Orbit around an object and check for missing materials.

        :param c: The controller.
        :param x: The next x positional coordinate.
        :param y: The next y positional coordinate.
        :param z: The next z positional coordinate.

        :return: True if there is a missing material in the image, False otherwise.
        """

        # Teleport the avatar.
        # Look at the model.
        # Receive an image.
        resp = c.communicate([{"$type": "teleport_avatar_to",
                               "position": {"x": x, "y": y, "z": z}},
                              {"$type": "look_at",
                               "object_id": MissingMaterials.OBJECT_ID,
                               "use_centroid": True}])

        # Check if there are any pink pixels.
        images = Images(resp[0])

        img = Image.open(BytesIO(images.get_image(0)))

        for c in img.getcolors(maxcolors=100000):
            if c[1] == MissingMaterials.HELL_PINK:
                return True
        return False

    @staticmethod
    def run(c: Controller) -> None:
        """
        Check every model for missing materials.

        :param c: The controller.
        """

        # Create a new output file.
        if MissingMaterials.OUTPUT_FILE.exists():
            MissingMaterials.OUTPUT_FILE.unlink()
        MissingMaterials.OUTPUT_FILE = str(MissingMaterials.OUTPUT_FILE.resolve())

        MissingMaterials.start(c)

        print(f"The names of models with missing materials will be saved to: {MissingMaterials.OUTPUT_FILE}")
        for library_path in ModelLibrarian.get_library_filenames():
            print(library_path)
            lib = ModelLibrarian(library=library_path)
            pbar = tqdm(total=len(lib.records))
            for record in lib.records:
                if record.do_not_use:
                    pbar.update(1)
                    continue
                pbar.set_description(record.name)
                # Check for missing materials.
                if MissingMaterials.materials_are_missing(c, record, record.get_url()):
                    with io.open(MissingMaterials.OUTPUT_FILE, "at") as f:
                        f.write("\n" + record.name)
                # Cleanup.
                c.communicate([{"$type": "destroy_object",
                                "id": MissingMaterials.OBJECT_ID},
                               {"$type": "unload_asset_bundles"}])
                pbar.update(1)
            pbar.close()
        c.communicate({"$type": "terminate"})


if __name__ == "__main__":
    MissingMaterials.run(Controller(launch_build=False))
