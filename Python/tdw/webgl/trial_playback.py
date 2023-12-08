from io import BytesIO
import re
import datetime
from platform import system
from typing import List, Union
from zipfile import ZipFile
from pathlib import Path
import numpy as np
from tdw.robot_data.robot_static import RobotStatic
from tdw.robot_data.joint_type import JointType
from tdw.tdw_utils import TDWUtils
from tdw.output_data import (OutputData, Version, Transforms, AvatarKinematic, AvatarNonKinematic, AvatarSimpleBody,
                             ImageSensors, AlbedoColors, Models, Scene, ObjectScales, PostProcess, FieldOfView,
                             ScreenSize, StaticRobot, DynamicRobots)
from tdw.add_ons.add_on import AddOn
from tdw.backend.platforms import SYSTEM_TO_S3


class TrialPlayback(AddOn):
    """
    An add-on that can be used to either read logged trial end-state information, or play it back in a non-physics controller.
    """

    _EPOCH: np.datetime64 = np.datetime64("00001-01-01T00:00")

    def __init__(self):
        """
        (no arguments)
        """

        super().__init__()
        """:field
        If True, a trial has been loaded.
        """
        self.loaded: bool = False
        """:field
        The name of the current trial.
        """
        self.name: str = ""
        """:field
        Whether the loaded trial ended in success or failure.
        """
        self.success: bool = False
        """:field
        The current frame of the loaded trial.
        """
        self.frame: int = 0
        """:field
        Per-frame output data.
        """
        self.frames: List[List[bytes]] = list()
        self.timestamps: List[np.datetime64] = list()
        self._avatar_ids: List[str] = list()
        self._static_robots: List[RobotStatic] = list()

    def load_file(self, path: Union[str, Path]) -> None:
        """
        Load a .zip file of trial playback data.

        :param path: The path to the .zip file.
        """

        with ZipFile(TDWUtils.get_string_path(path=path), "r") as z:
            self.read_zip(z=z)

    def read_bytes(self, bs: bytes) -> None:
        """
        Read .zip byte data.

        :param bs: A byte array of a trial playback .zip file.
        """

        with ZipFile(BytesIO(bs), "r") as z:
            self.read_zip(z=z)

    def read_zip(self, z: ZipFile) -> None:
        """
        Parse an opened .zip file. This will set `success`, `loaded`, `frame`, and `frames`.

        :param z: The zip file.
        """

        self.success = False
        self.frame = 0
        self.loaded = True
        self.frames.clear()
        self.timestamps.clear()
        self._avatar_ids.clear()
        self._static_robots.clear()
        # Get each frame.
        for fi in z.filelist:
            # Parse the metadata file.
            if fi.filename == "metadata":
                # Get the metadata.
                metadata: bytes = f.read()
                # Set the status.
                self.success = True if metadata[0] == 1 else 0
                # Decode the trial name.
                self.name = metadata[1:].decode("utf-8")
                continue
            # Iterate through each frame's output data.
            with z.open(fi.filename, "r") as f:
                # Read the frame data.
                frame: bytes = f.read()
                # Get the number of frame elements.
                num_elements: int = int.from_bytes(frame[0: 4], byteorder="little")
                offset: int = 4 + num_elements * 4
                # Get the output data elements.
                resp: List[bytes] = list()
                for i in range(num_elements):
                    # Get the length of the element.
                    element_length = int.from_bytes(frame[8 + i: 12 + i], byteorder="little")
                    resp.append(frame[offset: offset + element_length])
                    offset += element_length
                # Append the frame.
                self.frames.append(resp)
                # Append the timestamp.
                ticks = int.from_bytes(frame[-8:], byteorder="big")
                self.timestamps.append(TrialPlayback._EPOCH + np.timedelta64(ticks // 10, "us"))

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "simulate_physics",
                 "value": False}]

    def on_send(self, resp: List[bytes]) -> None:
        # Don't do anything if nothing is loaded.
        if not self.loaded:
            return
        resp: List[bytes] = self.frames[self.frame]
        # Convert output data into commands.
        for i in range(len(resp) - 2):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "scen":
                scene = Scene(resp[i])
                self.commands.append({"$type": "add_scene",
                                      "name": scene.get_name(),
                                      "url": TrialPlayback._get_asset_bundle_url(scene.get_url(), "scenes")})
            elif r_id == "mode":
                models = Models(resp[i])
                for j in range(models.get_num()):
                    self.commands.append({"$type": "add_object",
                                          "name": models.get_name(j),
                                          "url": TrialPlayback._get_asset_bundle_url(models.get_url(j), "models"),
                                          "id": models.get_id(j)})
            # Print the version.
            if r_id == "vers":
                version = Version(resp[i])
                print(version.get_tdw_version())
                print(version.get_unity_version())
            # Set the screen size.
            elif r_id == "scsi":
                screen_size = ScreenSize(resp[i])
                self.commands.append({"$type": "set_screen_size",
                                      "width": screen_size.get_width(),
                                      "height": screen_size.get_height()})
            # Teleport and rotate objects.
            elif r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    object_id = transforms.get_id(j)
                    self.commands.extend([{"$type": "teleport_object",
                                           "id": object_id,
                                           "position": TDWUtils.array_to_vector3(transforms.get_position(j))},
                                          {"$type": "rotate_object_to",
                                           "id": object_id,
                                           "rotation": TDWUtils.array_to_vector4(transforms.get_rotation(j))}])
            # Teleport and rotate an avatar.
            elif r_id == "avki":
                self._append_avatar_commands(avatar=AvatarKinematic(resp[i]))
            # Teleport and rotate an embodied avatar.
            elif r_id == "avsb":
                avatar = AvatarSimpleBody(resp[i])
                self._append_avatar_commands(avatar=avatar)
                # Set the body.
                self.commands.append({"$type": "change_avatar_body",
                                      "avatar_id": avatar.get_avatar_id(),
                                      "body_type": avatar.get_visible_body()})
            # Rotate a camera.
            elif r_id == "imse":
                image_sensors = ImageSensors(resp[i])
                avatar_id = image_sensors.get_avatar_id()
                for j in range(image_sensors.get_num_sensors()):
                    self.commands.append({"$type": "rotate_sensor_container_to",
                                          "avatar_id": avatar_id,
                                          "sensor_name": image_sensors.get_sensor_name(j),
                                          "rotation": TDWUtils.tuple_to_vector4(image_sensors.get_sensor_rotation(j))})
            # Set the color of each object.
            elif r_id == "acol":
                colors = AlbedoColors(resp[i])
                for j in range(colors.get_num()):
                    self.commands.append({"$type": "set_color",
                                          "id": colors.get_id(j),
                                          "color": TDWUtils.array_to_color(colors.get_color(j) / 255.0)})
            # Set object scales.
            elif r_id == "osca":
                scales = ObjectScales(resp[i])
                for j in range(scales.get_num()):
                    self.commands.append({"$type": "scale_object_to",
                                          "id": scales.get_id(j),
                                          "scale": TDWUtils.array_to_vector3(scales.get_scale(j))})
            # Set post-process values.
            elif r_id == "post":
                post_process = PostProcess(resp[i])
                # Disable post-process.
                if not post_process.get_enabled():
                    self.commands.append({"$type": "set_post_process",
                                          "value": False})
                    continue
                # Set post-process.
                self.commands.extend([{"$type": "set_ambient_occlusion_intensity",
                                       "intensity": post_process.get_ambient_occlusion_intensity()},
                                      {"$type": "set_ambient_occlusion_thickness_modifier",
                                       "thickness": post_process.get_ambient_occlusion_thickness_modifier()},
                                      {"$type": "set_aperture",
                                       "aperture": post_process.get_aperture()},
                                      {"$type": "set_focus_distance",
                                       "focus_distance": post_process.get_focus_distance()},
                                      {"$type": "set_contrast",
                                       "contrast": post_process.get_contrast()},
                                      {"$type": "set_post_exposure",
                                       "post_exposure": post_process.get_post_exposure()},
                                      {"$type": "set_saturation",
                                       "saturation": post_process.get_saturation()},
                                      {"$type": "set_screen_space_reflections",
                                       "enabled": post_process.get_screen_space_reflections()},
                                      {"$type": "set_vignette",
                                       "enabled": post_process.get_vignette()}])
            # Set an avatar's field of view.
            elif r_id == "fofv":
                field_of_view = FieldOfView(resp[i])
                self.commands.append({"$type": "set_field_of_view",
                                      "avatar_id": field_of_view.get_avatar_id(),
                                      "field_of_view": field_of_view.get_fov()})
            # Cache static robot data.
            elif r_id == "srob":
                static_robot = StaticRobot(resp[i])
                self._static_robots.append(RobotStatic(robot_id=static_robot.get_id(), resp=resp))
            # Set the positions of each robot joint.
            elif r_id == "drob":
                dynamic_robots = DynamicRobots(resp[i])
                for static in self._static_robots:
                    for joint_id in static.joints:
                        joint = static.joints[joint_id]
                        joint_index = joint.dynamic_index
                        angles = dynamic_robots.get_joint_angles(index=joint_index)[:joint.num_dof]
                        if joint.joint_type == JointType.revolute:
                            self.commands.append({"$type": "set_revolute_angle",
                                                  "angle": float(angles[0]),
                                                  "joint_id": joint_id,
                                                  "id": static.robot_id})
                        elif joint.joint_id == JointType.spherical:
                            self.commands.append({"$type": "set_spherical_angles",
                                                  "angles": TDWUtils.array_to_vector3(angles),
                                                  "joint_id": joint_id,
                                                  "id": static.robot_id})
                        elif joint.joint_id == JointType.prismatic:
                            self.commands.append({"$type": "set_prismatic_position",
                                                  "position": float(np.radians(angles[0])),
                                                  "joint_id": joint_id,
                                                  "id": static.robot_id})
        # Increment the frame count.
        self.frame += 1
        # Stop here.
        if self.frame >= len(self.frames):
            self.loaded = False

    def _append_avatar_commands(self, avatar: AvatarKinematic) -> None:
        """
        Append commands to teleport and rotate an avatar.

        :param avatar: The avatar output data.
        """

        avatar_id: str = avatar.get_avatar_id()
        # Create the avatar.
        if avatar_id not in self._avatar_ids:
            if isinstance(avatar, AvatarSimpleBody):
                avatar_type = "A_Simple_Body"
            elif isinstance(avatar, AvatarNonKinematic):
                avatar_type = "A_First_Person"
            else:
                avatar_type = "A_Img_Caps_Kinematic"
            self.commands.append({"$type": "create_avatar",
                                  "id": avatar_id,
                                  "type": avatar_type})
            self._avatar_ids.append(avatar_id)
        # Teleport and rotate the avatar.
        self.commands.extend([{"$type": "teleport_avatar_to",
                               "avatar_id": avatar_id,
                               "position": TDWUtils.tuple_to_vector3(avatar.get_position())},
                              {"$type": "rotate_avatar_to",
                               "avatar_id": avatar_id,
                               "position": TDWUtils.tuple_to_vector4(avatar.get_rotation())}])

    @staticmethod
    def _get_asset_bundle_url(url: str, infix: str) -> str:
        """
        :param url: The asset bundle URL.
        :param infix: The URL infix, e.g. models.

        :return: The asset bundle URL for this operating system.
        """

        # Convert the WebGL asset bundle to this platform's asset bundle.
        if url.startswith(f"https://tdw-public.s3.amazonaws.com/{infix}/webgl/"):
            return re.sub(r"(https://tdw-public.s3.amazonaws.com/)(.*?)(/webgl)(/.*)",
                          r"\1" + infix + "/" + SYSTEM_TO_S3[system()] + r"\4", url)
        else:
            return url
