from math import cos, sin, radians
from tdw.librarian import ModelRecord
from tdw.tdw_utils import TDWUtils
from tdw.model_pipeline.validator import Validator
from tdw.output_data import Images
from PIL import Image
from io import BytesIO
import numpy as np
from argparse import ArgumentParser
import json
from pathlib import Path


class PhysicsQualityWriter(Validator):
    """
    Assess the percentage of coverage by colliders on a model.
    Write the "physics quality" to the record.
    """

    def get_physics_quality(self) -> float:
        """
        Get the physics quality of the model.
        First, capture multiple images at different angles.
        Then, obscure the object with its own colliders and capture the same images.
        Compare the _id capture pass pixel count between each set of images.
        If the hull colliders obscure the entirety of the object in every image, physics_quality = 1.0
        """

        self.start()
        self.communicate([{"$type": "simulate_physics",
                           "value": False},
                          {"$type": "create_empty_environment"}])

        avatar_id = "A"
        delta_theta = 15

        print("Writing the physics quality to the record.")

        scale = TDWUtils.get_unit_scale(self.record)

        # Add the object.
        object_id = self.get_unique_id()
        self.communicate({"$type": "add_object",
                          "name": self.record.name,
                          "url": self.asset_bundle_path,
                          "scale_factor": self.record.scale_factor,
                          "id": object_id})

        # Scale the object to unit size.
        self.communicate({"$type": "scale_object",
                          "id": object_id,
                          "scale_factor": {"x": scale, "y": scale, "z": scale}})

        # Create the avatar.
        # Set the pass masks.
        self.communicate(TDWUtils.create_avatar(avatar_id=avatar_id))

        self.communicate({"$type": "set_pass_masks",
                          "avatar_id": avatar_id,
                          "pass_masks": ["_id"]})

        id_pass = []
        pink_pass = []
        for show_collider_hulls in [False, True]:
            x = 1.75
            y = 0.5
            z = 0

            # Show collider hulls.
            if show_collider_hulls:
                self.communicate({"$type": "show_collider_hulls",
                                  "id": object_id})

            # Reset the avatar.
            resp = self.communicate([{"$type": "teleport_avatar_to",
                                      "avatar_id": avatar_id,
                                      "position": {"x": x, "y": y, "z": z}},
                                     {"$type": "look_at",
                                      "avatar_id": avatar_id,
                                      "object_id": object_id,
                                      "use_centroid": True},
                                     {"$type": "send_images",
                                      "frequency": "always"}])

            # Equatorial orbit.
            theta = 0
            while theta < 360:
                # Get the number of pixels that aren't black.
                img = np.array(Image.open(BytesIO(Images(resp[0]).get_image(0))))
                grade = (256 * 256) - np.sum(np.all(img == np.array([0, 0, 0]), axis=2))

                if show_collider_hulls:
                    pink_pass.append(grade)
                else:
                    id_pass.append(grade)

                theta += delta_theta

                # Get the new position.
                rad = radians(theta)
                x1 = cos(rad) * x - sin(rad) * z
                z1 = sin(rad) * x + cos(rad) * z

                # Teleport the avatar.
                # Look at the object.
                resp = self.communicate([{"$type": "teleport_avatar_to",
                                          "avatar_id": avatar_id,
                                          "position": {"x": x1, "y": y, "z": z1}},
                                         {"$type": "look_at",
                                          "avatar_id": avatar_id,
                                          "object_id": object_id,
                                          "use_centroid": True}
                                         ])

            # Reset the avatar.
            resp = self.communicate([{"$type": "teleport_avatar_to",
                                      "avatar_id": avatar_id,
                                      "position": {"x": x, "y": y, "z": z}},
                                     {"$type": "look_at",
                                      "avatar_id": avatar_id,
                                      "object_id": object_id,
                                      "use_centroid": True},
                                     {"$type": "send_images",
                                      "frequency": "always"}])
            # Polar orbit.
            theta = 0
            while theta < 360:
                # Get the number of pixels that aren't black.
                img = np.array(Image.open(BytesIO(Images(resp[0]).get_image(0))))
                grade = (256 * 256) - np.sum(np.all(img == np.array([0, 0, 0]), axis=2))

                if show_collider_hulls:
                    pink_pass.append(grade)
                else:
                    id_pass.append(grade)

                theta += delta_theta

                # Get the new position.
                rad = radians(theta)
                x1 = cos(rad) * x - sin(rad) * z
                y1 = (sin(rad) * x + cos(rad) * z) + y

                # Teleport the avatar.
                # Look at the object.
                resp = self.communicate([{"$type": "teleport_avatar_to",
                                          "avatar_id": avatar_id,
                                          "position": {"x": x1, "y": y1, "z": 0}},
                                         {"$type": "look_at",
                                          "avatar_id": avatar_id,
                                          "object_id": object_id,
                                          "use_centroid": True}
                                         ])

        grades = [1 - (float(h) / float(i)) for h, i in zip(pink_pass, id_pass)]

        physics_quality = float(sum(grades)) / len(grades)
        print("Physics quality: " + str(physics_quality))

        # Kill the build.
        self.kill_build()
        return physics_quality


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--record_path", type=str, help="The path to the temporary record file")
    parser.add_argument("--asset_bundle_path", type=str, help="The path to the local asset bundle.")
    args = parser.parse_args()

    # Get the physics quality.
    c = PhysicsQualityWriter(record_path=args.record_path,
                             asset_bundle_path=args.asset_bundle_path)
    physics_quality = c.get_physics_quality()

    # Update the record.
    record_path = Path(args.record_path)
    record = ModelRecord(json.loads(record_path.read_text(encoding="utf-8")))
    record.physics_quality = physics_quality
    record_path.write_text(json.dumps(record.__dict__), encoding="utf-8")
