from time import time
from typing import List, Callable, Optional
from gzip import compress
import numpy as np
from PIL import Image, ImageChops
from struct import pack
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian
from tdw.output_data import OutputData, Images
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.webgl import TrialPlayback


class Playback(Controller):
    """
    This test measures the accuracy of a `TrialPlack` add-on in a standalone Unity context.

    This is a standalone Python controller.

    This controller runs the same simulation twice.

    In the first run, images are saved to disk. All other data is appended to a byte array in the same format as it is appended in a WebGL context.

    In the second run, the byte array of output data is fed to a `TrialPlayback` add-on, which recreates the scene in a non-physics context.
    Image capture is enabled. This controller measures discrepancies between the two runs by measuring the difference between each frame.
    We expect a *slight* difference due to how Unity post-processing and lighting works.

    This controller outputs the following to the console:

    - The size of the uncompressed data (MB)
    - The size of the compressed data (MB)
    - The TDW version
    - The Unity version
    - The average per-frame discrepancy. A number less than 1 should be considered to be negligible.
    """
    
    def __init__(self, num_frames: int = 3600, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate({"$type": "set_screen_size",
                          "width": 128,
                          "height": 128})
        self.directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("trial_playback_test")
        # This is the raw playback data.
        # The data added here is: byte order, length of metadata, trial success boolean, trial name
        self.raw_playback: bytearray = bytearray(b'\x01\x0b\x00\x00\x00\x01trial_name')
        self.num_frames: int = num_frames
        self.playback: Optional[TrialPlayback] = None
        self._differences: List[float] = list()

    def run(self, output_data_commands: List[dict],
            on_start: Callable[[List[dict]], List[bytes]],
            on_communicate: Callable[[int, List[bytes]], None],
            on_end: Callable[[], None]) -> None:
        # Initialize the scene. Get initial output data.
        resp = on_start(output_data_commands)
        # Do something with the initial output data.
        on_communicate(0, resp)
        # Run the simulation.
        for i in range(self.num_frames):
            resp = self.communicate([{"$type": "teleport_avatar_by",
                                      "position": {"x": 0.001, "y": 0, "z": 0.001}},
                                     {"$type": "rotate_sensor_container_by",
                                      "angle": 0.001,
                                      "axis": "yaw"}])
            on_communicate(i + 1, resp)
        on_end()

    def _create_scene(self, output_data_commands: List[dict]) -> List[bytes]:
        # Add the scene.
        scene_name = "box_room_2018"
        commands = [Controller.get_add_scene(scene_name=scene_name)]
        # Add the objects.
        scene_record = SceneLibrarian().get_record(scene_name)
        half_bounds: np.ndarray = np.array(scene_record.rooms[0].main_region.bounds) / 2
        s = 0.1
        grid_y = 4
        xs = np.linspace(-half_bounds[0], half_bounds[0], 5)
        ys = np.linspace(0, s * grid_y * 1.25, grid_y)
        zs = np.linspace(-half_bounds[2], half_bounds[2], 5)
        object_id = 0
        scale = {"x": s, "y": s, "z": s}
        force = {"x": 0, "y": 5, "z": -5}
        for x in xs:
            for y in ys:
                for z in zs:
                    # Add the object.
                    commands.extend(Controller.get_add_physics_object(model_name="octahedron",
                                                                      object_id=object_id,
                                                                      position={"x": float(x), "y": float(y), "z": float(z)},
                                                                      scale_factor=scale,
                                                                      scale_mass=False,
                                                                      default_physics_values=False,
                                                                      mass=0.5,
                                                                      dynamic_friction=0.1,
                                                                      static_friction=0.1,
                                                                      bounciness=0.8,
                                                                      library="models_flex.json"))
                    # Apply a force.
                    commands.append({"$type": "apply_force_to_object",
                                     "id": object_id,
                                     "force": force})
                    object_id += 1
        # Add the avatar.
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1.5, "z": float(-half_bounds[2]) + 0.1},
                                               look_at={"x": 0, "y": 0, "z": 0}))
        commands.append({"$type": "set_pass_masks",
                         "pass_masks": ["_img"]})
        # Append output data commands.
        commands.extend(output_data_commands)
        # Initialize the scene.
        return self.communicate(commands)

    def run_image_capture(self) -> None:
        output_data_commands = [{"$type": "send_version"},
                                {"$type": "send_framerate"},
                                {"$type": "send_screen_size"},
                                {"$type": "send_scene"},
                                {"$type": "send_post_process"},
                                {"$type": "send_avatar_ids"},
                                {"$type": "send_fast_avatars",
                                 "frequency": "always"},
                                {"$type": "send_fast_image_sensors",
                                 "frequency": "always"},
                                {"$type": "send_models"},
                                {"$type": "send_object_ids"},
                                {"$type": "send_scales"},
                                {"$type": "send_albedo_colors"},
                                {"$type": "send_fast_transforms",
                                 "frequency": "always"},
                                {"$type": "send_images",
                                 "frequency": "always"}]
        self.run(on_start=self._create_scene,
                 output_data_commands=output_data_commands,
                 on_communicate=self._on_capture_image,
                 on_end=self._on_image_capture_end)

    def run_playback(self) -> None:
        output_data_commands = [{"$type": "send_fast_avatars",
                                 "frequency": "never"},
                                {"$type": "send_fast_image_sensors",
                                 "frequency": "never"},
                                {"$type": "send_fast_transforms",
                                 "frequency": "never"},
                                {"$type": "send_images",
                                 "frequency": "never"}]
        self.run(on_start=self._playback_start,
                 output_data_commands=output_data_commands,
                 on_communicate=self._on_playback,
                 on_end=self._on_playback_end)

    def _on_capture_image(self, frame_count: int, resp: List[bytes]) -> None:
        # Add the number of elements.
        self.raw_playback.extend(pack("<i", len(resp) - 1))
        # Add the length of each element.
        for i in range(len(resp)):
            # Ignore images.
            if len(resp[i]) > 8:
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "imag":
                    continue
            # Append the length.
            self.raw_playback.extend(pack("<i", len(resp[i])))
        # Add each element.
        for i in range(len(resp)):
            if len(resp[i]) > 8:
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "imag":
                    # Save images.
                    TDWUtils.save_images(images=Images(resp[i]),
                                         filename=TDWUtils.zero_padding(frame_count, 4),
                                         output_directory=str(self.directory.resolve()),
                                         append_pass=False)
                    continue
            self.raw_playback.extend(resp[i])
        # Add the timestamp.
        # Source: https://stackoverflow.com/a/29368771
        self.raw_playback.extend(pack("<q", int(time() * 10**7)))

    def _on_image_capture_end(self) -> None:
        print("Uncompressed:", TDWUtils.bytes_to_megabytes(len(self.raw_playback)))
        compressed = compress(bytes(self.raw_playback))
        print("Compressed:", TDWUtils.bytes_to_megabytes(len(compressed)))
        # Write to disk.
        self.directory.joinpath("playback.gz").write_bytes(compressed)

    def _playback_start(self, output_data_commands: List[dict]) -> List[bytes]:
        self.playback = TrialPlayback()
        self.playback.load(self.directory.joinpath("playback.gz"))
        self.playback.initialized = True
        # Disable physics.
        commands = [{"$type": "simulate_physics",
                     "value": False}]
        commands.extend(output_data_commands)
        resp = self.communicate(commands)
        # Process the first frame.
        self.playback.on_send(resp=resp)
        self.playback.commands.append({"$type": "send_images",
                                       "frequency": "always"})
        # Send the commands.
        resp = self.communicate(self.playback.commands)
        # Append the add-on.
        self.add_ons.append(self.playback)
        return resp

    def _on_playback(self, frame_count: int, resp: List[bytes]) -> None:
        if frame_count == 0:
            return
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imag":
                playback_image = TDWUtils.get_pil_image(images=Images(resp[i]), index=0)
                # Get the corresponding saved image.
                saved_image = Image.open(str(self.directory.joinpath(TDWUtils.zero_padding(frame_count - 1) + ".png")))
                diff = ImageChops.difference(saved_image, playback_image)
                diff.save(str(self.directory.joinpath(f"diff_{TDWUtils.zero_padding(frame_count)}.png")))
                self._differences.append(float(np.sum(np.array(diff)) / (255 * diff.size[0] * diff.size[1])))
                break

    def _on_playback_end(self) -> None:
        print("Average per-pixel discrepancy:", sum(self._differences) / len(self._differences))
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Playback()
    c.run_image_capture()
    c.run_playback()
