import numpy as np
import random
import math
import zmq
import time
from scipy.spatial import distance
from tdw.output_data import IsOnNavMesh, Images, Bounds
from PIL import Image
import io
import os
from threading import Thread
from tdw.controller import Controller
from typing import List, Tuple, Dict, Optional, Union
import socket
from contextlib import closing
from tdw.librarian import ModelRecord
from pathlib import Path
import boto3
from botocore.exceptions import ProfileNotFound, ClientError
from subprocess import check_output, Popen, call
import re
from psutil import pid_exists
import base64


class TDWUtils:
    """
    Utility functions for controllers.

    Usage:

    ```python
    from tdw.tdw_utils import TDWUtils
    ```
    """

    VECTOR3_ZERO = {"x": 0, "y": 0, "z": 0}

    # Cached values used during point cloud generation.
    __WIDTH: int = -1
    __HEIGHT: int = -1
    __CAM_TO_IMG_MAT: Optional[np.array] = None

    @staticmethod
    def vector3_to_array(vector3: Dict[str, float]) -> np.array:
        """
        Convert a Vector3 object to a numpy array.

        :param vector3: The Vector3 object, e.g. `{"x": 0, "y": 0, "z": 0}`

        :return A numpy array.
        """

        return np.array([vector3["x"], vector3["y"], vector3["z"]])

    @staticmethod
    def array_to_vector3(arr: np.array) -> Dict[str, float]:
        """
        Convert a numpy array to a Vector3.

        :param arr: The numpy array.

        :return A Vector3, e.g. `{"x": 0, "y": 0, "z": 0}`
        """

        return {"x": float(arr[0]), "y": float(arr[1]), "z": float(arr[2])}

    @staticmethod
    def vector4_to_array(vector4: Dict[str, float]) -> np.array:
        """
        Convert a Vector4 to a numpy array.

        :param vector4: The Vector4 object, e.g. `{"x": 0, "y": 0, "z": 0, "w": 0}`

        :return A numpy array.
        """

        return np.array([vector4["x"], vector4["y"], vector4["z"], vector4["w"]])

    @staticmethod
    def array_to_vector4(arr: np.array) -> Dict[str, float]:
        """
        Convert a numpy array to a Vector4.

        :param arr: The numpy array.

        :return A Vector4, e.g. `{"x": 0, "y": 0, "z": 0, "w": 0}`
        """

        return {"x": arr[0], "y": arr[1], "z": arr[2], "w": arr[3]}

    @staticmethod
    def color_to_array(color: Dict[str, float]) -> np.array:
        """
        Convert a RGB Color to a numpy array.

        :param color: The Color object, e.g. `{"r": 0, "g": 0, "b": 0, "a": 1}`

        :return A numpy array.
        """

        return np.array([round(color["r"] * 255), round(color["g"] * 255), round(color["b"] * 255)])

    @staticmethod
    def array_to_color(arr: np.array) -> Dict[str, float]:
        """
        Convert a numpy array to a RGBA Color. If no A value is supplied it will default to 1.

        :param arr: The array.

        :return A Color, e.g. `{"r": 0, "g": 0, "b": 0, "a": 1}`
        """

        return {"r": arr[0], "g": arr[1], "b": arr[2], "a": 1 if len(arr) == 3 else arr[3]}

    @staticmethod
    def get_random_point_in_circle(center: np.array, radius: float) -> np.array:
        """
        Get a random point in a circle, defined by a center and radius.

        :param center: The center of the circle.
        :param radius: The radius of the circle.

        :return A numpy array. The y value (`arr[1]`) is always 0.
        """

        alpha = 2 * math.pi * random.random()
        r = radius * math.sqrt(random.random())
        x = r * math.cos(alpha) + center[0]
        z = r * math.sin(alpha) + center[2]

        return np.array([x, 0, z])

    @staticmethod
    def get_magnitude(vector3: Dict[str, float]) -> float:
        """
        Get the magnitude of a Vector3.

        :param vector3: The Vector3 object, e.g. `{"x": 0, "y": 0, "z": 0}`

        :return The vector magnitude.
        """

        return np.linalg.norm(TDWUtils.vector3_to_array(vector3))

    @staticmethod
    def extend_line(p0: np.array, p1: np.array, d: float, clamp_y=True) -> np.array:
        """
        Extend the line defined by p0 to p1 by distance d. Clamps the y value to 0.

        :param p0: The origin.
        :param p1: The second point.
        :param d: The distance of which the line is to be extended.
        :param clamp_y: Clamp the y value to 0.

        :return: The position at distance d.
        """

        if clamp_y:
            p0[1] = 0
            p1[1] = 0

        # Get the distance between the two points.
        d0 = distance.euclidean(p0, p1)
        # Get the total distance.
        d_total = d0 + d

        return p1 + ((p1 - p0) * d_total)

    @staticmethod
    def get_distance(vector3_0: Dict[str, float], vector3_1: Dict[str, float]) -> float:
        """
        Calculate the distance between two Vector3 (e.g. `{"x": 0, "y": 0, "z": 0}`) objects.

        :param vector3_0: The first Vector3.
        :param vector3_1: The second Vector3.

        :return The distance.
        """

        return distance.euclidean(TDWUtils.vector3_to_array(vector3_0), TDWUtils.vector3_to_array(vector3_1))

    @staticmethod
    def get_box(width: int, length: int) -> List[Dict[str, int]]:
        """
        Returns a list of x,y positions that can be used to create a box with the `create_exterior_walls` command.
        :param width: The width of the box.
        :param length: The length of the box.

        :return The box as represented by a list of `{"x": x, "y": y}` dictionaries.
        """

        box = []
        for x in range(width):
            for y in range(length):
                if x == 0 or x == width - 1 or y == 0 or y == length - 1:
                    box.append({"x": x, "y": y})
        return box

    @staticmethod
    def get_vector3(x, y, z) -> Dict[str, float]:
        """
        :param x: The x value.
        :param y: The y value.
        :param z: The z value.

        :return: A Vector3: {"x": x, "y", y, "z": z}
        """

        return {"x": x, "y": y, "z": z}

    @staticmethod
    def create_empty_room(width: int, length: int) -> dict:
        """
        :param width: The width of the room.
        :param length: The length of the room.

        :return: A `create_exterior_walls` command that creates a box with dimensions (width, length).
        """

        return {"$type": "create_exterior_walls", "walls": TDWUtils.get_box(width, length)}

    @staticmethod
    def create_room_from_image(filepath: str, exterior_color=(255, 0, 0), interior_color=(0, 0, 0)) -> List[dict]:
        """
        Load a .png file from the disk and use it to create a room. Each pixel on the image is a grid point.

        :param filepath: The absolute filepath to the image.
        :param exterior_color: The color on the image marking exterior walls (default=red).
        :param interior_color: The color on the image marking interior walls (default=black).

        :return: A list of commands: The first creates the exterior walls, and the second creates the interior walls.
        """

        exterior_walls = []
        interior_walls = []

        # Read the image.
        img = Image.open(filepath)
        pixels = img.load()
        col, row = img.size

        # Read each pixel as a grid point.
        for i in range(row):
            for j in range(col):
                pixel = pixels[i, j]
                if len(pixel) == 4:
                    pixel = (pixel[0], pixel[1], pixel[2])
                if pixel == exterior_color:
                    exterior_walls.append({"x": i, "y": col - j})
                elif pixel == interior_color:
                    interior_walls.append({"x": i, "y": col - j})

        return [{"$type": "create_exterior_walls",
                 "walls": exterior_walls},
                {"$type": "create_interior_walls",
                 "walls": interior_walls}]

    @staticmethod
    def save_images(images: Images, filename: str, output_directory="dist", resize_to=None, append_pass: bool = True) -> None:
        """
        Save each image in the Images object.
        The name of the image will be: pass_filename.extension, e.g.: `"0000"` -> `depth_0000.png`
        The images object includes the pass and extension information.

        :param images: The Images object. Contains each capture pass plus metadata.
        :param output_directory: The directory to write images to.
        :param filename: The filename of each image, minus the extension. The image pass will be appended as a prefix.
        :param resize_to: Specify a (width, height) tuple to resize the images to. This is slower than saving as-is.
        :param append_pass: If false, the image pass will _not_ be appended to the filename as a prefix, e.g.: `"0000"`: -> "`0000.jpg"`
        """

        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)

        for i in range(images.get_num_passes()):
            if append_pass:
                fi = images.get_pass_mask(i)[1:] + "_" + filename + "." + images.get_extension(i)
            else:
                fi = filename + "." + images.get_extension(i)

            if resize_to:
                TDWUtils.get_pil_image(images, i).resize((resize_to[0], resize_to[1]), Image.LANCZOS)\
                    .save(os.path.join(output_directory, fi))
            else:
                pass_mask = images.get_pass_mask(i)
                path = os.path.join(output_directory, fi)
                # The depth passes aren't png files, so we need to convert them.
                if pass_mask == "_depth" or pass_mask == "_depth_simple":
                    # Save the image.
                    Image.fromarray(TDWUtils.get_shaped_depth_pass(images=images, index=i)).save(path)
                # Every other pass can be saved directly to disk.
                else:
                    with open(path, "wb") as f:
                        f.write(images.get_image(i))

    @staticmethod
    def get_shaped_depth_pass(images: Images, index: int) -> np.array:
        """
        The `_depth` and `_depth_simple` passes are a 1D array of RGB values, as oppposed to a png or jpg like every other pass.
        This function reshapes the array into a 2D array of RGB values.

        :param images: The `Images` output data.
        :param index: The index in `Images` of the depth pass. See: `Images.get_pass_mask()`.

        :return: A reshaped depth pass. Shape is: `(height, width, 3)`.
        """

        return np.flip(np.reshape(images.get_image(index), (images.get_height(), images.get_width(), 3)), 0)

    @staticmethod
    def zero_padding(integer: int, width=4) -> str:
        """
        :param integer: The integer being converted.
        :param width: The total number of digits in the string. If integer == 3 and width == 4, output is: "0003".

        :return A string representation of an integer padded with zeroes, e.g. converts `3` to `"0003"`.
        """

        return str(integer).zfill(width)

    @staticmethod
    def get_pil_image(images: Images, index: int) -> Image:
        """
        Converts Images output data to a PIL Image object.
        Use this function to read and analyze an image in memory.
        Do NOT use this function to save image data to disk; `save_image` is much faster.

        :param images: Images data from the build.
        :param index: The index of the image in Images.get_image

        :return A PIL image.
        """

        return Image.open(io.BytesIO(images.get_image(index)))

    @staticmethod
    def get_random_position_on_nav_mesh(c: Controller, width: float, length: float, x_e=0, z_e=0, bake=True, rng=random.uniform) -> Tuple[float, float, float]:
        """
        Returns a random position on a NavMesh.

        :param c: The controller.
        :param width: The width of the environment.
        :param length: The length of the environment.
        :param bake: If true, send bake_nav_mesh.
        :param rng: Random number generator.
        :param x_e: The x position of the environment.
        :param z_e: The z position of the environment.

        :return The coordinates as a tuple `(x, y, z)`
        """

        if bake:
            c.communicate({'$type': 'bake_nav_mesh'})

        # Try to find a valid position on the NavMesh.
        is_on = False
        x, y, z = (0, 0, 0)
        while not is_on:
            # Get a random position.
            x = rng(-width / 2, width / 2) + x_e
            z = rng(-length / 2, length / 2) + z_e
            resp = c.communicate(
                {'$type': 'send_is_on_nav_mesh',
                 'position': {'x': x, 'y': 0, 'z': z},
                 'max_distance': 4.0
                 })
            answer = IsOnNavMesh(resp[0])
            is_on = answer.get_is_on()
            x, y, z = answer.get_position()
        return x, y, z

    @staticmethod
    def set_visual_material(c: Controller, substructure: List[dict], object_id: int, material: str, quality="med") -> List[dict]:
        """
        :param c: The controller.
        :param substructure: The metadata substructure of the object.
        :param object_id: The ID of the object in the scene.
        :param material: The name of the new material.
        :param quality: The quality of the material.

        :return A list of commands to set ALL visual materials on an object to a single material.
        """

        commands = []
        for sub_object in substructure:
            for i in range(len(sub_object["materials"])):
                commands.extend([c.get_add_material(material, library="materials_" + quality + ".json"),
                                 {"$type": "set_visual_material",
                                  "id": object_id,
                                  "material_name": material,
                                  "object_name": sub_object["name"],
                                  "material_index": i}])
        return commands

    @staticmethod
    def get_depth_values(image: np.array, depth_pass: str = "_depth", width: int = 256, height: int = 256, near_plane: float = 0.1, far_plane: float = 100) -> np.array:
        """
        Get the depth values of each pixel in a _depth image pass.
        The far plane is hardcoded as 100. The near plane is hardcoded as 0.1.
        (This is due to how the depth shader is implemented.)

        :param image: The image pass as a numpy array.
        :param depth_pass: The type of depth pass. This determines how the values are decoded. Options: `"_depth"`, `"_depth_simple"`.
        :param width: The width of the screen in pixels. See output data `Images.get_width()`.
        :param height: The height of the screen in pixels. See output data `Images.get_height()`.
        :param near_plane: The near clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the near clipping plane.
        :param far_plane: The far clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the far clipping plane.

        :return An array of depth values.
        """

        # Convert the image to a 2D image array.
        image = np.flip(np.reshape(image, (height, width, 3)), 0)
        if depth_pass == "_depth":
            depth_values = np.array((image[:, :, 0] + image[:, :, 1] / 256.0 + image[:, :, 2] / (256.0 ** 2)))
        elif depth_pass == "_depth_simple":
            depth_values = image[:, :, 0] / 256.0
        else:
            raise Exception(f"Invalid depth pass: {depth_pass}")
        # Un-normalize the depth values.
        return (depth_values * ((far_plane - near_plane) / 256.0)).astype(np.float32)

    @staticmethod
    def get_point_cloud(depth, camera_matrix: Union[np.array, tuple], vfov: float = 54.43222, filename: str = None, near_plane: float = 0.1, far_plane: float = 100) -> np.array:
        """
        Create a point cloud from an numpy array of depth values.

        :param depth: Depth values converted from a depth pass. See: `TDWUtils.get_depth_values()`
        :param camera_matrix: The camera matrix as a tuple or numpy array. See: [`send_camera_matrices`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#send_camera_matrices).
        :param vfov: The field of view. See: [`set_field_of_view`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_field_of_view)
        :param filename: If not None, the point cloud data will be written to this file.
        :param near_plane: The near clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the near clipping plane.
        :param far_plane: The far clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the far clipping plane.

        :return: An point cloud as a numpy array of `[x, y, z]` coordinates.
        """

        if isinstance(camera_matrix, tuple):
            camera_matrix = np.array(camera_matrix)
        camera_matrix = np.linalg.inv(camera_matrix.reshape((4, 4)))

        # Different from real-world camera coordinate system.
        # OpenGL uses negative z axis as the camera front direction.
        # x axes are same, hence y axis is reversed as well.
        # Source: https://learnopengl.com/Getting-started/Camera
        rot = np.array([[1, 0, 0, 0],
                        [0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [0, 0, 0, 1]])
        camera_matrix = np.dot(camera_matrix, rot)

        # Cache some calculations we'll need to use every time.
        if TDWUtils.__HEIGHT != depth.shape[0] or TDWUtils.__WIDTH != depth.shape[1]:
            TDWUtils.__HEIGHT = depth.shape[0]
            TDWUtils.__WIDTH = depth.shape[1]

            img_pixs = np.mgrid[0: depth.shape[0], 0: depth.shape[1]].reshape(2, -1)
            # Swap (v, u) into (u, v).
            img_pixs[[0, 1], :] = img_pixs[[1, 0], :]
            img_pix_ones = np.concatenate((img_pixs, np.ones((1, img_pixs.shape[1]))))

            # Calculate the intrinsic matrix from vertical_fov.
            # Motice that hfov and vfov are different if height != width
            # We can also get the intrinsic matrix from opengl's perspective matrix.
            # http://kgeorge.github.io/2014/03/08/calculating-opengl-perspective-matrix-from-opencv-intrinsic-matrix
            vfov = vfov / 180.0 * np.pi
            tan_half_vfov = np.tan(vfov / 2.0)
            tan_half_hfov = tan_half_vfov * TDWUtils.__WIDTH / float(TDWUtils.__HEIGHT)
            fx = TDWUtils.__WIDTH / 2.0 / tan_half_hfov  # focal length in pixel space
            fy = TDWUtils.__HEIGHT / 2.0 / tan_half_vfov
            intrinsics = np.array([[fx, 0, TDWUtils.__WIDTH / 2.0],
                                   [0, fy, TDWUtils.__HEIGHT / 2.0],
                                   [0, 0, 1]])
            img_inv = np.linalg.inv(intrinsics[:3, :3])
            TDWUtils.__CAM_TO_IMG_MAT = np.dot(img_inv, img_pix_ones)

        points_in_cam = np.multiply(TDWUtils.__CAM_TO_IMG_MAT, depth.reshape(-1))
        points_in_cam = np.concatenate((points_in_cam, np.ones((1, points_in_cam.shape[1]))), axis=0)
        points_in_world = np.dot(camera_matrix, points_in_cam)
        points_in_world = points_in_world[:3, :].reshape(3, TDWUtils.__WIDTH, TDWUtils.__HEIGHT)
        points_in_cam = points_in_cam[:3, :].reshape(3, TDWUtils.__WIDTH, TDWUtils.__HEIGHT)
        if filename is not None:
            f = open(filename, 'w')
            for i in range(points_in_world.shape[1]):
                for j in range(points_in_world.shape[2]):
                    if points_in_cam[2, i, j] < (far_plane - near_plane):
                        f.write(f'{points_in_world[0, i, j]};{points_in_world[1, i, j]};{points_in_world[2, i, j]}\n')
        return points_in_world

    @staticmethod
    def create_avatar(avatar_type="A_Img_Caps_Kinematic", avatar_id="a", position=None, look_at=None) -> List[dict]:
        """
        This is a wrapper for `create_avatar` and, optionally, `teleport_avatar_to` and `look_at_position`.

        :param avatar_type: The type of avatar.
        :param avatar_id: The avatar ID.
        :param position: The position of the avatar. If this is None, the avatar won't teleport.
        :param look_at: If this isn't None, the avatar will look at this position.

        :return A list of commands to create theavatar.
        """

        # Create the avatar.
        commands = [{"$type": "create_avatar",
                     "type": avatar_type,
                     "id": avatar_id}]

        # Teleport the avatar.
        if position:
            commands.append({"$type": "teleport_avatar_to",
                             "avatar_id": avatar_id,
                             "position": position})
        if look_at:
            commands.append({"$type": "look_at_position",
                             "avatar_id": avatar_id,
                             "position": look_at})
        return commands

    @staticmethod
    def _send_start_build(socket, controller_address: str) -> dict:
        """
        This sends a command to the launch_binaries daemon running on a remote node
        to start a binary connected to the given controller address.

        :param socket: The zmq socket.
        :param controller_address: The host name or ip address of node running the controller.

        :return Build info dictionary containing build port.
        """
        request = {"type": "start_build",
                   "controller_address": controller_address}
        socket.send_json(request)
        build_info = socket.recv_json()
        return build_info

    @staticmethod
    def _send_keep_alive(socket, build_info: dict) -> dict:
        """
        This sends a command to the launch_binaries daemon running on a remote node
        to mark a given binary as still alive, preventing garbage collection.

        :param socket: The zmq socket.
        :param build_info: A diciontary containing the build_port.

        :return a heartbeat indicating build is still alive.
        """

        build_port = build_info["build_port"]
        request = {"type": "keep_alive", "build_port": build_port}
        socket.send_json(request)
        heartbeat = socket.recv_json()
        return heartbeat

    @staticmethod
    def _send_kill_build(socket, build_info: dict) -> dict:
        """
        This sends a command to the launch_binaries daemon running on a remote node to terminate a given binary.

        :param socket: The zmq socket.
        :param build_info: A diciontary containing the build_port.

        :return A kill_status indicating build has been succesfully terminated.
        """

        build_port = build_info["build_port"]
        request = {"type": "kill_build", "build_port": build_port}
        socket.send_json(request)
        kill_status = socket.recv_json()
        return kill_status

    @staticmethod
    def _keep_alive_thread(socket, build_info: dict) -> None:
        """
        This is a wrapper around the keep alive command to be executed in a separate thread.

        :param socket: The zmq socket.
        :param build_info: A diciontary containing the build_port.
        """
        while True:
            TDWUtils._send_keep_alive(socket, build_info)
            time.sleep(60)

    @staticmethod
    def launch_build(listener_port: int, build_address: str, controller_address: str) -> dict:
        """
        Connect to a remote binary_manager daemon and launch an instance of a TDW build.

        Returns the necessary information for a local controller to connect.
        Use this function to automatically launching binaries on remote (or local) nodes, and to
        automatically shut down the build after controller is finished. Call in the constructor
        of a controller and pass the build_port returned in build_info to the parent Controller class.

        :param listener_port: The port launch_binaries is listening on.
        :param build_address: Remote IP or hostname of node running launch_binaries.
        :param controller_address: IP or hostname of node running controller.

        :return The build_info dictionary containing build_port.
        """

        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://" + build_address + ":%s" % listener_port)
        build_info = TDWUtils._send_start_build(socket, controller_address)
        thread = Thread(target=TDWUtils._keep_alive_thread,
                        args=(socket, build_info))
        thread.setDaemon(True)
        thread.start()
        return build_info

    @staticmethod
    def get_unity_args(arg_dict: dict) -> List[str]:
        """
        :param arg_dict: A dictionary of arguments. Key=The argument prefix (e.g. port) Value=Argument value.

        :return The formatted command line string that is accepted by unity arg parser.
        """

        formatted_args = []
        for key, value in arg_dict.items():
            prefix = "-" + key + "="
            if type(value) == list:
                prefix += ",".join([str(v) for v in value])
            else:
                prefix += str(value)
            formatted_args += [prefix]
        return formatted_args

    @staticmethod
    def find_free_port() -> int:
        """
        :return a free port.
        """

        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("", 0))
            return int(s.getsockname()[1])

    @staticmethod
    def get_unit_scale(record: ModelRecord) -> float:
        """
        :param record: The model record.

        :return The scale factor required to scale a model to 1 meter "unit scale".
        """

        bounds = record.bounds

        # Get the "unit scale" of the object.
        s = 1 / max(
            bounds['top']['y'] - bounds['bottom']['y'],
            bounds['front']['z'] - bounds['back']['z'],
            bounds['right']['x'] - bounds['left']['x'])
        return s

    @staticmethod
    def validate_amazon_s3() -> bool:
        """
        Validate that your local Amazon S3 credentials are set up correctly.

        :return True if everything is OK.
        """

        config_path = Path.home().joinpath(".aws/config")
        new_config_path = not config_path.exists()
        # Generate a valid config file.
        if new_config_path:
            config_path.write_text("[default]\nregion = us-east-1\noutput = json")
            print(f"Generated a new config file: {config_path.resolve()}")
        try:
            session = boto3.Session(profile_name="tdw")
            s3 = session.resource("s3")
            s3.meta.client.head_object(Bucket='tdw-private', Key='models/windows/2018-2019.1/iron_box')
            return True
        except ProfileNotFound:
            print(f"ERROR! Your AWS credentials file is not set up correctly.")
            print("Your AWS credentials must have a [tdw] profile with valid keys.")
            return False
        except ClientError as e:
            print("ERROR! Could not access bucket tdw-private. Make sure you have the right permissions.")
            error_code = e.response['Error']['Code']
            print(e, error_code)
            return False

    @staticmethod
    def get_base64_flex_particle_forces(forces: list) -> str:
        """
        :param forces: The forces (see Flex documentation for how to arrange this array).

        :return: An array of Flex particle forces encoded in base64.
        """

        forces = np.array(forces, dtype=np.float32)
        return base64.b64encode(forces).decode()

    @staticmethod
    def color_to_hashable(color: Union[np.array, Tuple[int, int, int]]) -> int:
        """
        :param color: The color as an RGB array or tuple, where each value is between 0 and 255.

        :return: A hashable integer representation of the color array.
        """

        return (color[0] << 16) + (color[1] << 8) + color[2]

    @staticmethod
    def hashable_to_color(hashable: int) -> np.array:
        """
        :param hashable: A hashable integer representing an RGB color.

        :return: A color as a numpy array of integers between 0 and 255: `[r, g, b]`
        """

        return np.array([(hashable >> 16) & 255, (hashable >> 8) & 255, hashable & 255], dtype=int)

    @staticmethod
    def get_bounds_dict(bounds: Bounds, index: int) -> Dict[str, np.array]:
        """
        :param bounds: Bounds output data.
        :param index: The index in `bounds` of the target object.

        :return: A dictionary of the bounds. Key = the name of the position. Value = the position as a numpy array.
        """

        return {"top": np.array(bounds.get_top(index)),
                "bottom": np.array(bounds.get_bottom(index)),
                "left": np.array(bounds.get_left(index)),
                "right": np.array(bounds.get_right(index)),
                "front": np.array(bounds.get_front(index)),
                "back": np.array(bounds.get_back(index)),
                "center": np.array(bounds.get_center(index))}

    @staticmethod
    def get_bounds_extents(bounds: Bounds, index: int) -> np.array:
        """
        :param bounds: Bounds output data.
        :param index: The index in `bounds` of the target object.

        :return: The width (left to right), length (front to back), and height (top to bottom) of the bounds as a numpy array.
        """

        return np.array([np.linalg.norm(np.array(bounds.get_left(index)) - np.array(bounds.get_right(index))),
                         np.linalg.norm(np.array(bounds.get_front(index)) - np.array(bounds.get_back(index))),
                         np.linalg.norm(np.array(bounds.get_top(index)) - np.array(bounds.get_bottom(index)))])

    @staticmethod
    def get_closest_position_in_bounds(origin: np.array, bounds: Bounds, index: int) -> np.array:
        """
        :param origin: The origin from which the distance is calculated.
        :param bounds: Bounds output data.
        :param index: The index in `bounds` of the target object.

        :return: The position on the object bounds that is closest to `origin`.
        """

        object_bounds = TDWUtils.get_bounds_dict(bounds=bounds, index=index)

        # Get the closest point on the bounds.
        min_destination = ""
        min_distance = 10000
        for p in object_bounds:
            d = np.linalg.norm(origin - object_bounds[p])
            if d < min_distance:
                min_distance = d
                min_destination = p
        return object_bounds[min_destination]

    @staticmethod
    def get_angle(forward: np.array, origin: np.array, position: np.array) -> float:
        """
          :param position: The target position.
          :param origin: The origin position of the directional vector.
          :param forward: The forward directional vector.

          :return: The angle in degrees between `forward` and the direction vector from `origin` to `position`.
          """

        # Get the normalized directional vector to the target position.
        p0 = np.array([origin[0], origin[2]])
        p1 = np.array([position[0], position[2]])
        d = p1 - p0
        d = d / np.linalg.norm(d)
        f = np.array([forward[0], forward[2]])

        dot = f[0] * d[0] + f[1] * d[1]
        det = f[0] * d[1] - f[1] * d[0]
        angle = np.arctan2(det, dot)
        angle = np.rad2deg(angle)
        return angle

    @staticmethod
    def get_angle_between(v1: np.array, v2: np.array) -> float:
        """
        :param v1: The first directional vector.
        :param v2: The second directional vector.

        :return: The angle in degrees between two directional vectors.
        """

        ang1 = np.arctan2(v1[2], v1[0])
        ang2 = np.arctan2(v2[2], v2[0])

        return np.rad2deg((ang1 - ang2) % (2 * np.pi))

    @staticmethod
    def rotate_position_around(position: np.array, angle: float, origin: np.array = None) -> np.array:
        """
        Rotate a position by a given angle around a given origin.

        :param origin: The origin position.  If None, the origin is `[0, 0, 0]`
        :param position: The point being rotated.
        :param angle: The angle in degrees.

        :return: The rotated position.
        """

        if origin is None:
            origin = np.array([0, 0, 0])

        radians = np.deg2rad(angle)
        x, y = position[0], position[2]
        offset_x, offset_y = origin[0], origin[2]
        adjusted_x = (x - offset_x)
        adjusted_y = (y - offset_y)
        cos_rad = np.cos(radians)
        sin_rad = np.sin(radians)
        qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
        qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

        return np.array([qx, position[1], qy])

    @staticmethod
    def euler_angles_to_rpy(euler_angles: np.array) -> np.array:
        """
        Convert Euler angles to ROS RPY angles.

        :param euler_angles: A numpy array: `[x, y, z]` Euler angles in degrees.

        :return: A numpy array: `[r, p, y]` angles in radians.
        """

        # Source: https://github.com/Unity-Technologies/URDF-Importer/blob/c41208565419b04907496baa93ad1b675d41dc20/com.unity.robotics.urdf-importer/Runtime/Extensions/TransformExtensions.cs#L85-L92
        return np.radians(np.array([-euler_angles[2], euler_angles[0], -euler_angles[1]]))


class AudioUtils:
    """
    Utility class for recording audio in TDW using [fmedia](https://stsaz.github.io/fmedia/).

    Usage:

    ```python
    from tdw.tdw_utils import AudioUtils
    from tdw.controller import Controller

    c = Controller()

    initialize_trial()  # Your code here.

    # Begin recording audio. Automatically stop recording at 10 seconds.
    AudioUtils.start(output_path="path/to/file.wav", until=(0, 10))

    do_trial()  # Your code here.

    # Stop recording.
    AudioUtils.stop()
    ```
    """

    # The process ID of the audio recorder.
    RECORDER_PID: Optional[int] = None
    # The audio capture device.
    DEVICE: Optional[str] = None

    @staticmethod
    def get_system_audio_device() -> str:
        """
        :return: The audio device that can be used to capture system audio.
        """

        devices = check_output(["fmedia", "--list-dev"]).decode("utf-8").split("Capture:")[1]
        dev_search = re.search("device #(.*): Stereo Mix", devices, flags=re.MULTILINE)
        assert dev_search is not None, "No suitable audio capture device found:\n" + devices
        return dev_search.group(1)

    @staticmethod
    def start(output_path: Union[str, Path], until: Optional[Tuple[int, int]] = None) -> None:
        """
        Start recording audio.

        :param output_path: The path to the output file.
        :param until: If not None, fmedia will record until `minutes:seconds`. The value must be a tuple of 2 integers. If None, fmedia will record until you send `AudioUtils.stop()`.
        """

        if isinstance(output_path, str):
            p = Path(output_path).resolve()
        else:
            p = output_path

        # Create the directory.
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        # Set the capture device.
        if AudioUtils.DEVICE is None:
            AudioUtils.DEVICE = AudioUtils.get_system_audio_device()
        fmedia_call = ["fmedia",
                       "--record",
                       f"--dev-capture={AudioUtils.DEVICE}",
                       f"--out={str(p.resolve())}",
                       "--globcmd=listen"]
        # Automatically stop recording.
        if until is not None:
            fmedia_call.append(f"--until={TDWUtils.zero_padding(until[0], 2)}:{TDWUtils.zero_padding(until[1], 2)}")
        with open(os.devnull, "w+") as f:
            AudioUtils.RECORDER_PID = Popen(fmedia_call,
                                            stderr=f).pid

    @staticmethod
    def stop() -> None:
        """
        Stop recording audio (if any fmedia process is running).
        """

        if AudioUtils.RECORDER_PID is not None:
            with open(os.devnull, "w+") as f:
                call(['fmedia', '--globcmd=quit'], stderr=f, stdout=f)
            AudioUtils.RECORDER_PID = None

    @staticmethod
    def is_recording() -> bool:
        """
        :return: True if the fmedia recording process still exists.
        """

        return AudioUtils.RECORDER_PID is not None and pid_exists(AudioUtils.RECORDER_PID)


class QuaternionUtils:
    """
    Helper functions for using quaternions.

    Quaternions are always numpy arrays in the following order: `[x, y, z, w]`.
    This is the order returned in all Output Data objects.

    Vectors are always numpy arrays in the following order: `[x, y, z]`.
    """

    """:class_var
    The global up directional vector.
    """
    UP = np.array([0, 1, 0])
    """:class_var
    The global forward directional vector.
    """
    FORWARD: np.array = np.array([0, 0, 1])
    """:class_var
    The quaternion identity rotation.
    """
    IDENTITY = np.array([0, 0, 0, 1])

    @staticmethod
    def get_inverse(q: np.array) -> np.array:
        """
        Source: https://referencesource.microsoft.com/#System.Numerics/System/Numerics/Quaternion.cs

        :param q: The quaternion.

        :return: The inverse of the quaternion.
        """

        x = q[0]
        y = q[1]
        z = q[2]
        w = q[3]

        ls = x * x + y * y + z * z + w * w
        inv = 1.0 / ls

        return np.array([-x * inv, -y * inv, -z * inv, w * inv])

    @staticmethod
    def multiply(q1: np.array, q2: np.array) -> np.array:
        """
        Multiply two quaternions.
        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q1: The first quaternion.
        :param q2: The second quaternion.
        :return: The multiplied quaternion: `q1 * q2`
        """

        x1 = q1[0]
        y1 = q1[1]
        z1 = q1[2]
        w1 = q1[3]

        x2 = q2[0]
        y2 = q2[1]
        z2 = q2[2]
        w2 = q2[3]

        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
        z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
        return np.array([x, y, z, w])

    @staticmethod
    def get_conjugate(q: np.array) -> np.array:
        """
        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q: The quaternion.

        :return: The conjugate of the quaternion: `[-x, -y, -z, w]`
        """

        x = q[0]
        y = q[1]
        z = q[2]
        w = q[3]

        return np.array([-x, -y, -z, w])

    @staticmethod
    def multiply_by_vector(q: np.array, v: np.array) -> np.array:
        """
        Multiply a quaternion by a vector.
        Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

        :param q: The quaternion.
        :param v: The vector.

        :return: A directional vector calculated from: `q * v`
        """

        q2 = (v[0], v[1], v[2], 0.0)
        return QuaternionUtils.multiply(QuaternionUtils.multiply(q, q2), QuaternionUtils.get_conjugate(q))[:-1]

    @staticmethod
    def world_to_local_vector(position: np.array, origin: np.array, rotation: np.array) -> np.array:
        """
        Convert a vector position in absolute world coordinates to relative local coordinates.
        Source: https://answers.unity.com/questions/601062/what-inversetransformpoint-does-need-explanation-p.html

        :param position: The position vector in world coordinates.
        :param origin: The origin vector of the local space in world coordinates.
        :param rotation: The rotation quaternion of the local coordinate space.

        :return: `position` in local coordinates.
        """

        return QuaternionUtils.multiply_by_vector(q=QuaternionUtils.get_inverse(q=rotation), v=position - origin)

    @staticmethod
    def get_up_direction(q: np.array) -> np.array:
        """
        :param q: The rotation as a quaternion.

        :return: A directional vector corresponding to the "up" direction from the quaternion.
        """

        return QuaternionUtils.multiply_by_vector(q, QuaternionUtils.UP)

    @staticmethod
    def euler_angles_to_quaternion(euler: np.array) -> np.array:
        """
        Convert Euler angles to a quaternion.

        :param euler: The Euler angles vector.

        :return: The quaternion representation of the Euler angles.
        """

        roll = euler[0]
        pitch = euler[1]
        yaw = euler[2]
        cy = np.cos(yaw * 0.5)
        sy = np.sin(yaw * 0.5)
        cp = np.cos(pitch * 0.5)
        sp = np.sin(pitch * 0.5)
        cr = np.cos(roll * 0.5)
        sr = np.sin(roll * 0.5)

        w = cy * cp * cr + sy * sp * sr
        x = cy * cp * sr - sy * sp * cr
        y = sy * cp * sr + cy * sp * cr
        z = sy * cp * cr - cy * sp * sr
        return np.array([x, y, z, w])

    @staticmethod
    def quaternion_to_euler_angles(quaternion: np.array) -> np.array:
        """
        Convert a quaternion to Euler angles.

        :param quaternion: A quaternion as a nump array.

        :return: The Euler angles representation of the quaternion.
        """

        x = quaternion[0]
        y = quaternion[1]
        z = quaternion[2]
        w = quaternion[3]
        ysqr = y * y

        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + ysqr)
        ex = np.degrees(np.arctan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = np.where(t2 > +1.0, +1.0, t2)

        t2 = np.where(t2 < -1.0, -1.0, t2)
        ey = np.degrees(np.arcsin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (ysqr + z * z)
        ez = np.degrees(np.arctan2(t3, t4))

        return np.array([ex, ey, ez])

    @staticmethod
    def get_y_angle(q1: np.array, q2: np.array) -> float:
        """
        Source: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

        :param q1: The first quaternion.
        :param q2: The second quaternion.

        :return: The angle between the two quaternions in degrees around the y axis.
        """

        qd = QuaternionUtils.multiply(QuaternionUtils.get_conjugate(q1), q2)

        return np.rad2deg(2 * np.arcsin(qd[1]))
