from time import sleep
from argparse import ArgumentParser
from json import dumps
from typing import List, Dict
import numpy as np
from tqdm import tqdm
from tdw.librarian import SceneLibrarian
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.scene_data.scene_bounds import SceneBounds
from tdw.output_data import OutputData, Raycast, Images, Version
from tdw.backend.paths import PLAYER_LOG_PATH, EDITOR_LOG_PATH, ASSET_BUNDLE_VERIFIER_OUTPUT_DIR


class _AvatarPosition:
    """
    The position of the avatar and the rotation of its image sensor.
    """

    def __init__(self, position: Dict[str, float], pitch: float, yaw: float):
        """
        :param position: The position of the avatar.
        :param pitch: The pitch angle.
        :param yaw: The yaw angle.
        """

        self.position: Dict[str, float] = position
        self.pitch: float = pitch
        self.yaw: float = yaw


class _SceneLog:
    """
    A log of a scene.
    """

    def __init__(self, log: List[str], positions: List[_AvatarPosition]):
        """
        :param log: Any new messages that appeared in the Unity log after creating the scene.
        :param positions: A list of avatar positions that captured an image with pink pixels (missing materials).
        """

        self.log: List[str] = log
        self.positions: List[_AvatarPosition] = positions

    def to_dict(self) -> dict:
        return {"log": self.log, "positions": [p.__dict__ for p in self.positions]}


class SceneVerifier(Controller):
    """
    Check each scene for logged errors and missing materials.
    """

    # The output path.
    PATH = ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.joinpath("scenes.json")
    # These are single rooms in which we can just use the StreamedSceneBounds.
    SINGLE_ROOMS: List[str] = ["abandoned_factory", "box_room_2018", "building_site", "dead_grotto", "iceland_beach",
                               "lava_field", "monkey_physics_room", "ruin", "tdw_room"]
    # The Unity pink color that appears when there is a missing material.
    PINK: np.ndarray = np.array([255, 0, 255])

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # Set a relatively large screen and make sure we're using the max render quality.
        self.communicate([{"$type": "set_screen_size",
                           "width": 256,
                           "height": 256},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_post_process",
                           "value": False},
                          {"$type": "set_img_pass_encoding",
                           "value": True}])

    def run(self) -> None:
        """
        Load each scene.
        Teleport the avatar to predefined positions.
        At each position, rotate the sensor container 360 degrees, capturing image data.
        Check each image for missing materials.
        """

        print(f"Results will be saved to: {SceneVerifier.PATH}")

        # Get the version.
        resp = self.communicate({"$type": "send_version"})
        # Get the log path depending on whether this is a standalone build.
        log_path = PLAYER_LOG_PATH if Version(resp[0]).get_standalone() else EDITOR_LOG_PATH
        logged_text = log_path.read_text(encoding="utf-8")

        if "scenes.json" not in Controller.SCENE_LIBRARIANS:
            Controller.SCENE_LIBRARIANS["scenes.json"] = SceneLibrarian()
        lib = Controller.SCENE_LIBRARIANS["scenes.json"]
        pbar = tqdm(total=len(lib.records))
        result: Dict[str, _SceneLog] = dict()
        # Iterate through each scene record.
        for record in lib.records:
            if record.name == "suburb_scene_2018":
                continue
            pbar.set_description(record.name)
            # Clear the add-ons from the previous trial.
            self.add_ons.clear()
            # Add the camera.
            camera = ThirdPersonCamera(avatar_id="a")
            self.add_ons.append(camera)
            # Load the scene. Get the scene bounds.
            resp = self.communicate([Controller.get_add_scene(record.name),
                                     {"$type": "send_scene_regions"}])
            scene_bounds = SceneBounds(resp=resp)

            # Wait a bit for text to be logged.
            sleep(5)
            # Diff the log.
            logged_text_1 = log_path.read_text(encoding="utf-8")
            logged_scene = logged_text_1.replace(logged_text, "")
            logged_text = logged_text_1
            # Get avatar positions.
            scene_positions: List[_AvatarPosition] = list()
            # If this is a floorplan, mm_, or single-room scene, we can use the scene bounds.
            if record.name.startswith("floorplan_") or record.name.startswith("mm_") or record.name in SceneVerifier.SINGLE_ROOMS:
                # Iterate through each region.
                for region in scene_bounds.regions:
                    # Get the center of the region and set the y coordinate.
                    position_arr = np.array(region.center)
                    position_arr[1] = 2.1
                    position: Dict[str, float] = TDWUtils.array_to_vector3(position_arr)
                    # Look at positions in a circle.
                    a: float = 0
                    da: float = 30
                    while a < 360:
                        scene_positions.append(_AvatarPosition(position=position, pitch=15, yaw=a))
                        a += da
            # We only need one image for the empty scene.
            elif record.name == "empty_scene":
                scene_positions.append(_AvatarPosition(position=TDWUtils.VECTOR3_ZERO.copy(), pitch=0, yaw=0))
            elif record.name == "downtown_alleys":
                scene_positions.extend(self._get_positions(avatar_positions=[{"x": 0, "y": 0, "z": -5.27},
                                                                             {"x": 9.23, "y": 0, "z": 4.67},
                                                                             {"x": 30.4, "y": 0, "z": -0.32}]))
            elif record.name == "suburb_scene_2023":
                y = 2.5
                scene_positions.extend(self._get_positions(avatar_positions=[{"x": 0, "y": y, "z": 0},
                                                                             {"x": -34, "y": y, "z": 0},
                                                                             {"x": 34, "y": y, "z": 0},
                                                                             {"x": 58, "y": y, "z": 21},
                                                                             {"x": 58, "y": y, "z": -21},
                                                                             {"x": -58, "y": y, "z": 21},
                                                                             {"x": -58, "y": y, "z": -21}]))
            elif record.name == "archviz_house":
                y = 1.8
                scene_positions.extend(self._get_positions(avatar_positions=[{"x": -14, "y": y, "z": 0},
                                                                             {"x": -12.83, "y": y, "z": -5},
                                                                             {"x": -6, "y": y, "z": -0.24},
                                                                             {"x": -6, "y": y, "z": -0.24},
                                                                             {"x": -1.77, "y": 1.12, "z": -1.9},
                                                                             {"x": 2.19, "y": y, "z": -6.24},
                                                                             {"x": 2.19, "y": 3.6, "z": -2.4},
                                                                             {"x": -1.89, "y": 3.6, "z": -0.85}]))
            elif record.name == "savanna_6km":
                r: int = 500
                xs = np.arange(int(scene_bounds.x_min) + r, int(scene_bounds.x_max), step=r)
                zs = np.arange(int(scene_bounds.z_min) + r, int(scene_bounds.z_max), step=r)
                y = 500
                avatar_positions: List[Dict[str, float]] = list()
                # Raycast to get valid positions.
                for x in xs:
                    for z in zs:
                        xf = float(x)
                        zf = float(z)
                        resp = self.communicate({"$type": "send_raycast",
                                                 "origin": {"x": xf, "y": y, "z": zf},
                                                 "destination": {"x": xf, "y": -y, "z": zf}})
                        for i in range(len(resp) - 1):
                            r_id = OutputData.get_data_type_id(resp[i])
                            if r_id == "rayc":
                                raycast = Raycast(resp[i])
                                if raycast.get_hit():
                                    avatar_position = TDWUtils.array_to_vector3(np.array(raycast.get_point()))
                                    avatar_position["y"] = 60
                                    avatar_positions.append(avatar_position)
                scene_positions.extend(self._get_positions(avatar_positions=avatar_positions))
            else:
                print(f"Warning! Positions not defined for: {record.name}")
            # Prepare image capture.
            self.communicate([{"$type": "set_pass_masks",
                               "pass_masks": ["_img"],
                               "avatar_id": "a"},
                              {"$type": "send_images",
                               "frequency": "always",
                               "ids": ["a"]}])
            # Teleport and rotate the camera. Get images.
            pink_positions: List[_AvatarPosition] = list()
            for p in scene_positions:
                # Teleport and rotate.
                resp = self.communicate([{"$type": "teleport_avatar_to",
                                          "position": p.position},
                                         {"$type": "rotate_sensor_container_by",
                                          "axis": "pitch",
                                          "angle": p.pitch},
                                         {"$type": "rotate_sensor_container_by",
                                          "axis": "yaw",
                                          "angle": p.yaw}])
                self.communicate({"$type": "reset_sensor_container_rotation"})
                # Look for pink pixels.
                for j in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[j])
                    if r_id == "imag":
                        image = np.array(TDWUtils.get_pil_image(Images(resp[j]), 0))
                        for pixel in image:
                            if np.array_equal(pixel, SceneVerifier.PINK):
                                pink_positions.append(p)
                                break
                        break
            result[record.name] = _SceneLog(log=logged_scene, positions=pink_positions)
            self.communicate({"$type": "send_images",
                              "frequency": "never"})
            pbar.update(1)
        q = dict()
        for n in result:
            q[n] = [result[n].to_dict()]
        SceneVerifier.PATH.write_text(dumps(q, indent=2, sort_keys=True))
        self.communicate({"$type": "terminate"})

    @staticmethod
    def _get_positions(avatar_positions: List[Dict[str, float]]) -> List[_AvatarPosition]:
        scene_positions: List[_AvatarPosition] = list()
        for position in avatar_positions:
            # Rotate the sensor container in a circle.
            a: float = 0
            da: float = 30
            while a < 360:
                scene_positions.append(_AvatarPosition(position=position, pitch=20,  yaw=a))
                a += da
        return scene_positions


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--download", type=str,
                        help="Download the scenes.")
    parser.add_argument("--library", type=str,
                        help="The path to the local scene library.")
    args = parser.parse_args()
    # Download the scene asset bundles.
    if args.download is not None:
        TDWUtils.download_asset_bundles(path=args.download,
                                        scenes={"scenes.json": [record.name for record in SceneLibrarian().records]})
        exit()
    # Set a local librarian.
    if args.library is not None:
        Controller.SCENE_LIBRARIANS["scenes.json"] = SceneLibrarian(args.library)
    c = SceneVerifier()
    c.run()
