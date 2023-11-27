from typing import List, Union
from zipfile import ZipFile
from json import loads
from pathlib import Path
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, AvatarKinematic, AvatarSimpleBody, ImageSensors
from tdw.add_ons.add_on import AddOn
from tdw.webgl.frame import Frame


class TrialPlayback(AddOn):
    """
    An add-on that can be used to either read logged trial end-state information, or play it back in a non-physics controller.
    """

    def __init__(self):
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
        Per-frame commands sent and output data received.
        """
        self.frames: List[Frame] = list()

    def load_file(self, path: Union[str, Path]) -> None:
        """
        Load a .zip file of trial playback data.

        :param path: The path to the .zip file.
        """

        with ZipFile(TDWUtils.get_string_path(path=path), "r") as z:
            self.read_zip(z=z)

    def read_zip(self, z: ZipFile) -> None:
        """
        Parse an opened .zip file. This will set `success`, `loaded`, `frame` and `frames`.

        :param z: The zip file.
        """

        self.success = False
        self.frame = 0
        self.loaded = True
        self.frames.clear()
        with z.open("metadata", "r") as f:
            # Get the metadata.
            metadata: bytes = f.read()
            # Set the status.
            self.success = True if metadata[0] == 1 else 0
            # Decode the trial name.
            self.name = metadata[1:].decode("utf-8")
        # Get each frame.
        for fi in z.filelist:
            if fi.filename == "metadata":
                continue
            with z.open(fi.filename, "r") as f:
                # Read the frame data.
                frame: bytes = f.read()
                # Get the number of frame elements.
                num_elements: int = int.from_bytes(frame[0: 4], byteorder="little")
                offset: int = 4 + num_elements * 4
                # Get the length of the commands element.
                commands_length: int = int.from_bytes(frame[4: 8], byteorder="little")
                # Get the commands.
                commands: List[dict] = loads(frame[offset: offset + commands_length])
                offset += commands_length
                # Get the output data elements.
                resp: List[bytes] = list()
                for i in range(num_elements - 1):
                    # Get the length of the element.
                    element_length = int.from_bytes(frame[8 + i: 12 + i], byteorder="little")
                    resp.append(frame[offset: offset + element_length])
                    offset += element_length
                # Append the frame.
                self.frames.append(Frame(commands=commands, resp=resp))

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "simulate_physics",
                 "value": False}]

    def on_send(self, resp: List[bytes]) -> None:
        # Don't do anything if nothing is loaded.
        if not self.loaded:
            return
        frame: Frame = self.frames[self.frame]
        # Append the frame's commands.
        self.commands.extend(frame.commands)
        # Convert output data into commands.
        for i in range(len(frame.resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Teleport and rotate objects.
            if r_id == "tran":
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
        self.commands.extend([{"$type": "teleport_avatar_to",
                               "avatar_id": avatar_id,
                               "position": TDWUtils.tuple_to_vector3(avatar.get_position())},
                              {"$type": "rotate_avatar_to",
                               "avatar_id": avatar_id,
                               "position": TDWUtils.tuple_to_vector4(avatar.get_rotation())}])
