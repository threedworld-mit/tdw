from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import IdPassGrayscale, Images, ImageSensors, Environments, OutputData, Transforms
from tdw.librarian import ModelLibrarian, MaterialLibrarian, HDRISkyboxLibrarian, ModelRecord, HDRISkyboxRecord
import numpy as np
from tqdm import tqdm
import os
from subprocess import call
from secrets import token_urlsafe
from pathlib import Path
import json
from datetime import datetime
from threading import Thread
from time import time
from typing import List, Dict


RNG = np.random.RandomState(0)


class ImagePosition:
    """
    Data to stage an image.
    """

    def __init__(self, avatar_position: dict,
                 camera_rotation: dict,
                 object_position: dict,
                 object_rotation: dict):
        """
        :param avatar_position: The position of the avatar as a Vector3.
        :param camera_rotation: The rotation of the avatar as a Quaternion.
        :param object_position: The position of the object as a Vector3.
        :param object_rotation: The rotation of the object as a Quaternion.
        """

        self.avatar_position = avatar_position
        self.camera_rotation = camera_rotation
        self.object_position = object_position
        self.object_rotation = object_rotation


class Environment:
    """
    Environment data for a single environment.
    """

    def __init__(self, envs: Environments, e: int):
        """
        :param envs: The environments data.
        :param e: The index of this environment.
        """

        self.x, y, self.z = envs.get_center(e)
        self.w, self.h, self.l = envs.get_bounds(e)


class SingleObject(Controller):
    def __init__(self,
                 port=1071,
                 launch_build=False,
                 visual_material_swapping=False,
                 new=False,
                 screen_size=256,
                 output_size=256,
                 hdri=False,
                 show_objects=True,
                 clamp_rotation=False,
                 max_height=1.0,
                 grayscale_threshold=0.5,
                 less_dark=False,
                 id_pass=False,
                 no_overwrite=False,
                 do_zip=False,
                 train=1300000,
                 val=50000,
                 library="models_full.json",
                 temp_urls: bool = False):
        """
        :param port: The port used to connect to the build.
        :param launch_build: If True, automatically launch the build. Always set this to False on a Linux server.
        :param visual_material_swapping: If true, set random visual materials per frame.
        :param new: If true, clear the list of models that have already been used.
        :param screen_size: The screen size of the build.
        :param output_size: The size of the output images.
        :param hdri: If true, use a random HDRI skybox per frame.
        :param show_objects: If true, show objects.
        :param clamp_rotation: If true, clamp the rotation to +/- 30 degrees around each axis.
        :param max_height: The percentage of the environment height that is the ceiling for the avatar and object. Must be between 0 and 1.
        :param grayscale_threshold: The grayscale threshold. Higher value = slower FPS, better composition. Must be between 0 and 1.
        :param less_dark: If true, there will be more daylight exterior skyboxes (requires hdri == True)
        :param id_pass: If true, send the _id pass.
        :param no_overwrite: If true, don't overwrite images.
        :param do_zip: If true, zip the directory at the end.
        :param train: Number of train images.
        :param val: Number of val images.
        :param library: The path to the library records file.
        """

        self.screen_size = screen_size
        self.output_size = output_size
        self.show_objects = show_objects
        self.clamp_rotation = clamp_rotation
        self.max_height = max_height
        self.grayscale_threshold = grayscale_threshold
        self.id_pass = id_pass
        self.no_overwrite = no_overwrite
        self.do_zip = do_zip
        self.train = train
        self.val = val

        assert 0 < max_height <= 1.0, f"Invalid max height: {max_height}"
        assert 0 < grayscale_threshold <= 1.0, f"Invalid grayscale threshold: {grayscale_threshold}"

        self.less_dark = less_dark

        self.substructures: Dict[str, List[dict]] = {}

        self.new = new

        super().__init__(port=port, launch_build=launch_build)

        self.model_librarian = ModelLibrarian(library=library)
        self.material_librarian = MaterialLibrarian("materials_high.json")
        self.hdri_skybox_librarian = HDRISkyboxLibrarian()

        # Get material records.
        if visual_material_swapping:
            self.materials = self.material_librarian.records
        else:
            self.materials = None

        # Get skybox records.
        if hdri:
            self.skyboxes = self.hdri_skybox_librarian.records

            # Prefer exterior daytime skyboxes by adding them multiple times to the list.
            if self.less_dark:
                temp = self.skyboxes[:]
                for skybox in temp:
                    if skybox.location != "interior" and skybox.sun_elevation >= 145:
                        self.skyboxes.append(skybox)
        else:
            self.skyboxes = None

        # Download from pre-signed URLs.
        if temp_urls:
            self.communicate({"$type": "use_pre_signed_urls",
                              "value": True})

    def initialize_scene(self, scene_command, a="a") -> list:
        """
        Initialize the scene.

        :param scene_command: The command to load the scene.
        :param a: The avatar ID.
        :return: The Environments data of the scene.
        """

        # Initialize the scene.
        # Add the avatar.
        commands = [scene_command,
                    {"$type": "create_avatar",
                     "type": "A_Img_Caps_Kinematic",
                     "id": a,
                     "envs": [0]}]
        # Disable physics.
        # Enable jpgs.
        # Set FOV.
        # Set clipping planes.
        # Set AA.
        # Set aperture.
        # Disable vignette.
        commands.extend([{"$type": "simulate_physics",
                          "value": False},
                         {"$type": "set_img_pass_encoding",
                          "value": False},
                         {'$type': 'set_field_of_view',
                          'avatar_id': 'a',
                          'field_of_view': 60},
                         {'$type': 'set_camera_clipping_planes',
                          'avatar_id': 'a',
                          'far': 160,
                          'near': 0.01},
                         {"$type": "set_anti_aliasing",
                          "avatar_id": "a",
                          "mode": "subpixel"},
                         {"$type": "set_aperture",
                          "aperture": 70},
                         {'$type': 'set_vignette',
                          'enabled': False}])

        # If we're using HDRI skyboxes, send additional favorable post-process commands.
        if self.skyboxes is not None:
            commands.extend([{"$type": "set_post_exposure",
                              "post_exposure": 0.6},
                             {"$type": "set_contrast",
                              "contrast": -20},
                             {"$type": "set_saturation",
                              "saturation": 10},
                             {"$type": "set_screen_space_reflections",
                              "enabled": False},
                             {"$type": "set_shadow_strength",
                              "strength": 1.0}])

        # Send the commands.
        self.communicate(commands)

        # Get the environments data.
        env_data = Environments(self.communicate({"$type": "send_environments",
                                                  "frequency": "once"})[0])
        envs = []
        for i in range(env_data.get_num()):
            envs.append(Environment(env_data, i))
        return envs

    def generate_metadata(self, dataset_dir: str, scene_name: str) -> None:
        """
        Generate a metadata file for this dataset.

        :param dataset_dir: The dataset directory for images.
        :param scene_name: The scene name.
        """

        root_dir = f"{dataset_dir}/images/"
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        data = {"dataset": dataset_dir,
                "scene": scene_name,
                "train": self.train,
                "val": self.val,
                "visual_material_swapping": self.materials is not None,
                "hdri": self.skyboxes is not None,
                "screen_size": self.screen_size,
                "output_size": self.output_size,
                "clamp_rotation": self.clamp_rotation,
                "show_objects": self.show_objects,
                "max_height": self.max_height,
                "grayscale_threshold": self.grayscale_threshold,
                "less_dark": self.less_dark,
                "multi_scene": self.no_overwrite,
                "start": datetime.now().strftime("%H:%M %d.%m.%y")
                }
        with open(os.path.join(root_dir, "metadata.txt"), "wt") as f:
            json.dump(data, f, sort_keys=True, indent=4)

    def run(self, dataset_dir: str, scene_name: str) -> None:
        """
        Generate the dataset.

        :param dataset_dir: The dataset directory for images.
        :param scene_name: The scene name.
        """

        # Create the metadata file.
        self.generate_metadata(dataset_dir,
                               scene_name=scene_name)
        
        # The root directory of the output.
        root_dir = f"{dataset_dir}/images/"
        
        # The avatar ID.
        a = "a"

        # Initialize the scene.
        envs = self.initialize_scene(self.get_add_scene(scene_name))

        # Fetch the WordNet IDs.
        wnids = self.model_librarian.get_model_wnids()
        # Remove any wnids that don't have valid models.
        wnids = [w for w in wnids if len(
            [r for r in self.model_librarian.get_all_models_in_wnid(w) if not r.do_not_use]) > 0]

        # Set the number of train and val images per wnid.
        num_train = self.train / len(wnids)
        num_val = self.val / len(wnids)

        # Create the progress bar.
        pbar = tqdm(total=len(wnids))

        # If this is a new dataset, remove the previous list of completed models.
        done_models_filename = "processed_records.txt"
        if self.new and os.path.exists(done_models_filename):
            os.remove(done_models_filename)

        # Get a list of models that have already been processed.
        processed_model_names = []
        if os.path.exists(done_models_filename):
            with open(done_models_filename, "rt") as f:
                txt = f.read()
                processed_model_names = txt.split("\n")

        # Iterate through each wnid.
        for w, q in zip(wnids, range(len(wnids))):
            # Update the progress bar.
            pbar.set_description(w)

            # Get all valid models in the wnid.
            records = self.model_librarian.get_all_models_in_wnid(w)
            records = [r for r in records if not r.do_not_use]

            # Get the train and val counts.
            train_count = [len(a) for a in np.array_split(
                np.arange(num_train), len(records))][0]
            val_count = [len(a) for a in np.array_split(
                np.arange(num_val), len(records))][0]

            # Process each record.
            fps = "nan"
            for record, i in zip(records, range(len(records))):
                # Set the progress bar description to the wnid and FPS.
                pbar.set_description(f"record {i + 1}/{len(records)}, FPS {fps}")

                # Skip models that have already been processed.
                if record.name in processed_model_names:
                    continue

                # Create all of the images for this model.
                dt = self.process_model(record, a, envs, train_count, val_count, root_dir, w)
                fps = round((train_count + val_count) / dt)

                # Mark this record as processed.
                with open(done_models_filename, "at") as f:
                    f.write(f"\n{record.name}")

            pbar.update(1)
        pbar.close()

        # Add the end time to the metadata file.
        with open(os.path.join(root_dir, "metadata.txt"), "rt") as f:
            data = json.load(f)
            end_time = datetime.now().strftime("%H:%M %d.%m.%y")
            if "end" in data:
                data["end"] = end_time
            else:
                data.update({"end": end_time})
        with open(os.path.join(root_dir, "metadata.txt"), "wt") as f:
            json.dump(data, f, sort_keys=True, indent=4)

        # Terminate the build.
        if not self.no_overwrite:
            self.communicate({"$type": "terminate"})
        # Zip up the images.
        if self.do_zip:
            zip_dir = Path(dataset_dir)
            SingleObject.zip_images(zip_dir)

    def set_skybox(self, records: List[HDRISkyboxRecord], its_per_skybox: int, hdri_index: int, skybox_count: int) -> (int, int, dict):
        """
        If it's time, set a new skybox.

        :param records: All HDRI records.
        :param its_per_skybox: Iterations per skybox.
        :param hdri_index: The index in the records list.
        :param skybox_count: The number of images of this model with this skybox.
        :return: (hdri_index, skybox_count, command used to set the skybox)
        """

        # Set a new skybox.
        if skybox_count == 0:
            command = self.get_add_hdri_skybox(records[hdri_index].name)
        # It's not time yet to set a new skybox. Don't send a command.
        else:
            command = None
        skybox_count += 1
        if skybox_count >= its_per_skybox:
            hdri_index += 1
            if hdri_index >= len(records):
                hdri_index = 0
            skybox_count = 0
        return hdri_index, skybox_count, command

    def process_model(self, record: ModelRecord, a: str, envs: list, train_count: int, val_count: int,
                      root_dir: str, wnid: str) -> float:
        """
        Capture images of a model.

        :param record: The model record.
        :param a: The ID of the avatar.
        :param envs: All environment data.
        :param train_count: Number of train images.
        :param val_count: Number of val images.
        :param root_dir: The root directory for saving images.
        :param wnid: The wnid of the record.
        :return The time elapsed.
        """

        image_count = 0

        # Get the filename index. If we shouldn't overwrite any images, start after the last image.
        if self.no_overwrite:
            # Check if any images exist.
            wnid_dir = Path(root_dir).joinpath(f"train/{wnid}")
            if wnid_dir.exists():
                max_file_index = -1
                for image in wnid_dir.iterdir():
                    if not image.is_file() or image.suffix != ".jpg" \
                            or not image.stem.startswith("img_") or image.stem[4:-5] != record.name:
                        continue
                    image_index = int(image.stem[-4:])
                    if image_index > max_file_index:
                        max_file_index = image_index
                file_index = max_file_index + 1
            else:
                file_index = 0
        else:
            file_index = 0

        image_positions = []
        o_id = self.get_unique_id()

        s = TDWUtils.get_unit_scale(record)

        # Add the object.
        # Set the screen size to 32x32 (to make the build run faster; we only need the average grayscale values).
        # Toggle off pass masks.
        # Set render quality to minimal.
        # Scale the object to "unit size".
        self.communicate([{"$type": "add_object",
                           "name": record.name,
                           "url": record.get_url(),
                           "scale_factor": record.scale_factor,
                           "category": record.wcategory,
                           "id": o_id},
                          {"$type": "set_screen_size",
                           "height": 32,
                           "width": 32},
                          {"$type": "set_pass_masks",
                           "avatar_id": a,
                           "pass_masks": []},
                          {"$type": "set_render_quality",
                           "render_quality": 0},
                          {"$type": "scale_object",
                           "id": o_id,
                           "scale_factor": {"x": s, "y": s, "z": s}}])

        # The index in the HDRI records array.
        hdri_index = 0
        # The number of iterations on this skybox so far.
        skybox_count = 0
        if self.skyboxes:
            # The number of iterations per skybox for this model.
            its_per_skybox = round((train_count + val_count) / len(self.skyboxes))

            # Set the first skybox.
            hdri_index, skybox_count, command = self.set_skybox(self.skyboxes, its_per_skybox, hdri_index, skybox_count)
            self.communicate(command)
        else:
            its_per_skybox = 0

        while len(image_positions) < train_count + val_count:
            e = RNG.choice(envs)

            # Get the real grayscale.
            g_r, d, a_p, o_p, o_rot, cam_rot = self.get_real_grayscale(o_id, a, e)

            if g_r > 0:
                # Get the optimal grayscale.
                g_o = self.get_optimal_grayscale(o_id, a, o_p, a_p)

                if g_o > 0 and g_r / g_o > self.grayscale_threshold:
                    # Cache the position.
                    image_positions.append(ImagePosition(a_p, cam_rot, o_p, o_rot))

        # Send images.
        # Set the screen size.
        # Set render quality to maximum.
        commands = [{"$type": "send_images",
                     "frequency": "always"},
                    {"$type": "set_pass_masks",
                     "avatar_id": a,
                     "pass_masks": ["_img", "_id"] if self.id_pass else ["_img"]},
                    {"$type": "set_screen_size",
                     "height": self.screen_size,
                     "width": self.screen_size},
                    {"$type": "set_render_quality",
                     "render_quality": 5}]
        # Hide the object maybe.
        if not self.show_objects:
            commands.append({"$type": "hide_object",
                             "id": o_id})

        self.communicate(commands)

        t0 = time()

        # Generate images from the cached spatial data.
        train = 0
        for p in image_positions:
            # Teleport the avatar.
            # Rotate the avatar's camera.
            # Teleport the object.
            # Rotate the object.
            # Get the response.
            commands = [{"$type": "teleport_avatar_to",
                         "avatar_id": a,
                         "position": p.avatar_position},
                        {"$type": "rotate_sensor_container_to",
                         "avatar_id": a,
                         "rotation": p.camera_rotation},
                        {"$type": "teleport_object",
                         "id": o_id,
                         "position": p.object_position},
                        {"$type": "rotate_object_to",
                         "id": o_id,
                         "rotation": p.object_rotation}]
            # Set the visual materials.
            if self.materials is not None:
                if record.name not in self.substructures:
                    self.substructures.update({record.name: record.substructure})
                for sub_object in self.substructures[record.name]:
                    for i in range(len(self.substructures[record.name][sub_object["name"]])):
                        material_name = self.materials[RNG.randint(0, len(self.materials))].name
                        commands.extend([self.get_add_material(material_name),
                                         {"$type": "set_visual_material",
                                          "id": o_id,
                                          "material_name": material_name,
                                          "object_name": sub_object["name"],
                                          "material_index": i}])
            # Maybe set a new skybox.
            # Rotate the skybox.
            if self.skyboxes:
                hdri_index, skybox_count, command = self.set_skybox(self.skyboxes, its_per_skybox, hdri_index, skybox_count)
                if command:
                    commands.append(command)
                commands.append({"$type": "rotate_hdri_skybox_by",
                                 "angle": RNG.uniform(0, 360)})

            resp = self.communicate(commands)

            # Create a thread to save the image.
            t = Thread(target=self.save_image, args=(resp, record, file_index, root_dir, wnid, train, train_count))
            t.daemon = True
            t.start()
            train += 1
            file_index += 1
            image_count += 1
        t1 = time()

        # Stop sending images.
        # Destroy the object.
        # Unload asset bundles.
        self.communicate([{"$type": "send_images",
                           "frequency": "never"},
                          {"$type": "destroy_object",
                           "id": o_id},
                          {"$type": "unload_asset_bundles"}])
        return t1 - t0

    def save_image(self, resp, record: ModelRecord, image_count: int, root_dir: str, wnid: str, train: int, train_count: int) -> None:
        """
        Save an image.

        :param resp: The raw response data.
        :param record: The model record.
        :param image_count: The image count.
        :param root_dir: The root directory.
        :param wnid: The wnid.
        :param train: Number of train images so far.
        :param train_count: Total number of train images to generate.
        """
        
        # Get the directory.
        directory = Path(root_dir).joinpath("train" if train < train_count else "val").joinpath(wnid).resolve()
        if not os.path.exists(directory):
            # Try to make the directories. Due to threading, they might already be made.
            try:
                os.makedirs(directory)
            except:
                pass

        # Save the image.
        filename = f"{record.name}_{image_count:04d}"

        # Save the image without resizing.
        if self.screen_size == self.output_size:
            TDWUtils.save_images(Images(resp[0]), filename,
                                 output_directory=directory)
        # Resize the image and save it.
        else:
            TDWUtils.save_images(Images(resp[0]), filename,
                                 output_directory=directory,
                                 resize_to=(self.output_size, self.output_size))

    def get_optimal_grayscale(self, o_id: int, a_id: str, o_p: dict, a_p: dict) -> float:
        """
        Get the "optimal" grayscale value of the object if there wasn't any occlusion.

        :param o_id: The ID of the object.
        :param a_id: The ID of the avatar.
        :param o_p: The position of the object.
        :param a_p: The position of the avatar.
        :return: The grayscale value.
        """

        # Teleport the object into the sky.
        # Teleport the avatar into the sky.
        # Return the grayscale value.
        return IdPassGrayscale(self.communicate([{"$type": "teleport_object",
                                                  "id": o_id,
                                                  "position": {"x": o_p["x"],
                                                               "y": o_p["y"] + 500,
                                                               "z": o_p["z"]}},
                                                 {"$type": "teleport_avatar_to",
                                                  "avatar_id": a_id,
                                                  "position": {"x": a_p["x"],
                                                               "y": a_p["y"] + 500,
                                                               "z": a_p["z"]}},
                                                 {"$type": "send_id_pass_grayscale",
                                                  "frequency": "once"}
                                                 ])[0]).get_grayscale()

    def get_real_grayscale(self, o_id: int, a_id: str, e: Environment) -> (float, float, dict, dict, dict, dict):
        """
        Get the "real" grayscale value of an image we hope to capture.

        :param o_id: The ID of the object.
        :param a_id: The ID of the avatar.
        :param e: The environment.
        
        :return: (grayscale, distance, avatar_position, object_position, object_rotation, avatar_rotation)
        """

        # Get a random position for the avatar.
        a_p = np.array([RNG.uniform(-e.w / 2, e.w / 2) + e.x,
                        RNG.uniform(0.4, e.h * self.max_height),
                        RNG.uniform(-e.l / 2, e.l / 2) + e.z])

        # Get a random distance from the avatar.
        d = RNG.uniform(0.8, 3)

        # Get a random position for the object constrained to the environment bounds.
        o_p = SingleObject.sample_spherical() * d
        # Clamp the y value to positive.
        o_p[1] = abs(o_p[1])
        o_p = a_p + o_p

        # Clamp the y value of the object.
        if o_p[1] > e.h * self.max_height:
            o_p[1] = e.h * self.max_height

        # Convert the avatar's position to a Vector3.
        a_p = TDWUtils.array_to_vector3(a_p)

        # Set random camera rotations.
        yaw = RNG.uniform(-15, 15)
        pitch = RNG.uniform(-15, 15)

        # Convert the object position to a Vector3.
        o_p = TDWUtils.array_to_vector3(o_p)

        # Add rotation commands.
        # If we're clamping the rotation, rotate the object within +/- 30 degrees on each axis.
        if self.clamp_rotation:
            o_rot = None
            commands = [{"$type": "rotate_object_to",
                         "id": o_id,
                         "rotation": {"x": 0, "y": 0, "z": 0, "w": 0}},
                        {"$type": "rotate_object_by",
                         "id": o_id,
                         "angle": RNG.uniform(-30, 30),
                         "axis": "pitch"},
                        {"$type": "rotate_object_by",
                         "id": o_id,
                         "angle": RNG.uniform(-30, 30),
                         "axis": "yaw"},
                        {"$type": "rotate_object_by",
                         "id": o_id,
                         "angle": RNG.uniform(-30, 30),
                         "axis": "roll"}]
        # Set a totally random rotation.
        else:
            o_rot = {"x": RNG.uniform(-360, 360),
                     "y": RNG.uniform(-360, 360),
                     "z": RNG.uniform(-360, 360),
                     "w": RNG.uniform(-360, 360),
                     }
            commands = [{"$type": "rotate_object_to",
                         "id": o_id,
                         "rotation": o_rot}]

        # After rotating the object:
        # 1. Teleport the object.
        # 2. Teleport the avatar.
        # 3. Look at the object.
        # 4. Perturb the camera slightly.
        # 5. Send grayscale data and image sensor data.
        commands.extend([{"$type": "teleport_object",
                          "id": o_id,
                          "position": o_p},
                         {"$type": "teleport_avatar_to",
                          "avatar_id": a_id,
                          "position": a_p},
                         {"$type": "look_at",
                          "avatar_id": a_id,
                          "object_id": o_id,
                          "use_centroid": True},
                         {"$type": "rotate_sensor_container_by",
                          "angle": pitch,
                          "avatar_id": "a",
                          "axis": "pitch"},
                         {"$type": "rotate_sensor_container_by",
                          "angle": yaw,
                          "avatar_id": "a",
                          "axis": "yaw"},
                         {"$type": "send_id_pass_grayscale",
                          "frequency": "once"},
                         {"$type": "send_image_sensors",
                          "frequency": "once"}])

        resp = self.communicate(commands)

        # Parse the output data:
        # 1. The grayscale value of the image.
        # 2. The camera rotation.
        grayscale = 0
        cam_rot = None
        for r in resp[:-1]:
            r_id = OutputData.get_data_type_id(r)
            if r_id == "idgs":
                grayscale = IdPassGrayscale(r).get_grayscale()
            elif r_id == "imse":
                cam_rot = ImageSensors(r).get_sensor_rotation(0)
                cam_rot = {"x": cam_rot[0], "y": cam_rot[1], "z": cam_rot[2], "w": cam_rot[3]}

        # If we clamped the rotation of the object, we need to know its quaternion.
        if self.clamp_rotation:
            resp = self.communicate({"$type": "send_transforms",
                                     "frequency": "once",
                                     "ids": [o_id]})
            t = Transforms(resp[0])
            o_rot = t.get_rotation(0)
            o_rot = {"x": o_rot[0],
                     "y": o_rot[1],
                     "z": o_rot[2],
                     "w": o_rot[3],}

        return grayscale, d, a_p, o_p, o_rot, cam_rot

    @staticmethod
    def sample_spherical(npoints=1, ndim=3) -> np.array:
        vec = RNG.randn(ndim, npoints)
        vec /= np.linalg.norm(vec, axis=0)
        return np.array([vec[0][0], vec[1][0], vec[2][0]])

    @staticmethod
    def zip_images(zip_dir: Path) -> None:
        """
        Zip up the images.

        :param zip_dir: The zip directory.
        """

        if not zip_dir.exists():
            zip_dir.mkdir()

        # Use a random token to avoid overwriting zip files.
        token = token_urlsafe(4)
        zip_path = zip_dir.joinpath(f"images_{token}.zip")
        images_directory = str(zip_dir.joinpath("images").resolve())

        # Create the zip file. If it is made, remove the original directory.
        zip_call = f'C:/Program Files/7-Zip/7z.exe a -r {str(zip_path.resolve())} {images_directory} -sdel'
        call(zip_call)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--scene_name", type=str, default="tdw_room",
                        help="The name of the scene. For a complete list: librarian.fetch_all_scene_records()")
    parser.add_argument("--output_dir", type=str, default="D:/Test",
                        help="The absolute path to the output directory.")
    parser.add_argument("--materials", action="store_true", help="Set random visual materials per frame.")
    parser.add_argument("--new", action="store_true", help="Start a new dataset (erases the log of completed models).")
    parser.add_argument("--screen_size", type=int, default=256, help="The screen size of the build.")
    parser.add_argument("--output_size", type=int, default=256, help="Images are resized to this from the screen size.")
    parser.add_argument("--hdri", action="store_true", help="Use a random HDRI skybox per frame.")
    parser.add_argument("--hide", action="store_true", help="Hide all objects.")
    parser.add_argument("--clamp_rotation", action="store_true",
                        help="Clamp rotation to +/- 30 degrees on each axis, rather than totally random.")
    parser.add_argument("--port", type=int, default=1071, help="The port for the controller and build.")
    parser.add_argument("--launch_build", action="store_true",
                        help="Automatically launch the build. "
                             "Don't add this if you're running the script on a Linux server.")
    parser.add_argument("--max_height", type=float, default=1,
                        help="Objects and avatars can be at this percentage of the scene bounds height. Must be between 0 and 1.")
    parser.add_argument("--grayscale", type=float, default=0.5,
                        help="Target grayscale value. Must be between 0 and 1. Higher value = better composition and slower FPS.")
    parser.add_argument("--less_dark", action="store_true", help='Prefer fewer "dark" skyboxes.')
    parser.add_argument("--id_pass", action="store_true", help="Include the _id pass.")
    parser.add_argument("--no_overwrite", action="store_true",
                        help="If true, don't overwrite existing images, and start indexing after the highest index.")
    parser.add_argument("--zip", action="store_true",
                        help="Zip the images after finishing the dataset. Requires Windows and 7zip.")
    parser.add_argument("--train", type=int, default=1300000, help="Total number of train images.")
    parser.add_argument("--val", type=int, default=50000, help="Total number of val images.")
    parser.add_argument("--library", type=str, default="models_core.json", help="The path to the model library records.")
    parser.add_argument("--temp_urls", action="store_true",
                        help="If included and `--library models_full.json`, the build will use temporary (pre-signed) "
                             "URLs to download models in the tdw-private bucket. "
                             "Include this flag only if you're experiencing segfaults on Linux.")
    args = parser.parse_args()

    s = SingleObject(port=args.port,
                     launch_build=args.launch_build,
                     visual_material_swapping=args.materials,
                     new=args.new,
                     screen_size=args.screen_size,
                     output_size=args.output_size,
                     hdri=args.hdri,
                     show_objects=not args.hide,
                     clamp_rotation=args.clamp_rotation,
                     max_height=args.max_height,
                     grayscale_threshold=args.grayscale,
                     less_dark=args.less_dark,
                     id_pass=args.id_pass,
                     no_overwrite=args.no_overwrite,
                     do_zip=args.zip,
                     train=args.train,
                     val=args.val,
                     library=args.library,
                     temp_urls=args.temp_urls is not None)
    s.run(args.output_dir,
          scene_name=args.scene_name)
