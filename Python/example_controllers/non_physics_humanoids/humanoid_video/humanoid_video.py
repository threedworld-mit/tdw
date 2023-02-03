from tdw.controller import Controller
from tdw.librarian import SceneLibrarian, SceneRecord, HumanoidLibrarian, HumanoidAnimationLibrarian, HumanoidRecord, \
    HumanoidAnimationRecord, HDRISkyboxLibrarian, HDRISkyboxRecord
from tdw.output_data import Images, Transforms
from tdw.tdw_utils import TDWUtils
from tdw.version import __version__
import numpy as np
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from typing import List, Optional, Dict
import json


class _AnimationAndScene:
    """
    Metadata for an animation and a scene.
    """

    def __init__(self, animation: HumanoidAnimationRecord,
                 scene: SceneRecord,
                 position: Dict[str, float] = TDWUtils.VECTOR3_ZERO,
                 rotation: Dict[str, float] = TDWUtils.VECTOR3_ZERO):
        """
        :param scene: The scene record.
        :param animation: The animation record.
        :param position: The initial position of the humanoid as a Vector3 dictionary.
        :param rotation: The initial rotation of the humanoid in Euler angles as a Vector3 dictionary.
        """

        self.animation = animation
        self.scene = scene
        self.position = position
        self.rotation = rotation


class HumanoidVideo(Controller):
    """
    For a given number of videos, create animations of humanoids.
    """

    RNG = np.random.RandomState(0)

    def __init__(self, root_dir: Path):
        animation_lib = HumanoidAnimationLibrarian()
        scene_lib = SceneLibrarian()
        animation_scene_matrix = json.loads(Path("animation_scene_matrix.json").read_text())
        self.animations_and_scenes: List[_AnimationAndScene] = []
        for a in animation_scene_matrix:
            for s in animation_scene_matrix[a]:
                combo = _AnimationAndScene(animation=animation_lib.get_record(a),
                                           scene=scene_lib.get_record(s),
                                           position=animation_scene_matrix[a][s]["position"],
                                           rotation=animation_scene_matrix[a][s]["rotation"])
                self.animations_and_scenes.append(combo)
        super().__init__()
        self.root_dir = root_dir
        if not self.root_dir.exists():
            self.root_dir.mkdir(parents=True)

        # Set global values.
        self.communicate([{"$type": "set_render_quality",
                           "render_quality": 5},
                          {"$type": "set_img_pass_encoding",
                           "value": False},
                          {"$type": "set_shadow_strength",
                           "strength": 1.0},
                          {"$type": "set_screen_size",
                           "width": 1280,
                           "height": 720}])

    def get_video(self,
                  a_and_s: _AnimationAndScene,
                  humanoids: List[HumanoidRecord],
                  skyboxes: List[HDRISkyboxRecord],
                  pbar: Optional[tqdm] = None,
                  num_camera_iterations: int = 1,
                  h_id: int = 0,
                  min_duration: float = 2.5,
                  overwrite: bool = False) -> None:
        """
        Create a single animation video as a series of images that will be written to the disk.

        :param a_and_s: The animation/scene combo.
        :param humanoids: The humanoid records. Iterate through all of these.
        :param skyboxes: The HDRI skyboxes. Iterate through some of these (equal to num_camera_iterations).
        :param pbar: The progress bar (optional).
        :param num_camera_iterations: Make this many videos of each specific animation/humanoid/scene/skybox combo, changing the camera angle each time.
        :param h_id: The object ID of the humanoid.
        :param min_duration: The minimum duration of the video in seconds.
        :param overwrite: If True, overwrite existing images.
        """

        # Skip some frames to maintain 30 FPS.
        save_per = a_and_s.animation.framerate / 30

        # Randomize the skyboxes without randomizing the original list.
        skyboxes_temp = skyboxes[:]
        HumanoidVideo.RNG.shuffle(skyboxes_temp)
        assert num_camera_iterations < len(skyboxes_temp), f"Number of camera iterations ({num_camera_iterations})" \
                                                           f" exceeds number of skyboxes ({len(skyboxes_temp)}"

        # Determine how many times to loop the animation.
        total_duration = 0
        num_loops = 0
        while total_duration < min_duration:
            num_loops += 1
            total_duration += a_and_s.animation.duration

        for humanoid in humanoids:
            for i in range(num_camera_iterations):
                name = a_and_s.animation.name + "-" + a_and_s.scene.name + "-" + humanoid.name + "-" + str(i)
                # Prepare the output directory for the images.
                output_dir = self.root_dir.joinpath(name)
                metadata_path = output_dir.joinpath("metadata.json")

                # Skip a completed video.
                if metadata_path.exists() and not overwrite:
                    if pbar is not None:
                        pbar.update(1)
                    continue

                if not output_dir.exists():
                    output_dir.mkdir(parents=True)
                output_dir = str(output_dir.resolve())

                # Add a skybox if this scene is HDRI-enabled and exterior.
                add_skybox = a_and_s.scene.hdri and a_and_s.scene.location == "exterior"
                skybox = skyboxes_temp.pop(0)

                if pbar is not None:
                    pbar.set_description(name)

                # Per-frame, focus on the object and look at the object.
                # Pitch the camera slightly upward so that it isn't pointing at the stomach.
                per_frame_commands = [{"$type": "focus_on_object",
                                       "object_id": h_id,
                                       "use_centroid": True},
                                      {"$type": "look_at",
                                       "object_id": h_id,
                                       "use_centroid": True},
                                      {"$type": "rotate_sensor_container_by",
                                       "axis": "pitch",
                                       "angle": -5},
                                      {"$type": "send_images",
                                       "frequency": "once"}]

                # Write metadata to disk.
                metadata = {"humanoid": humanoid.name,
                            "animation": a_and_s.animation.name,
                            "scene": a_and_s.scene.name,
                            "location": a_and_s.scene.location,
                            "skybox": skybox.name if add_skybox else "",
                            "datetime": str(datetime.now()),
                            "tdw_version": __version__}

                # Load the scene, avatar, and humanoid.
                # Play the animation and begin image capture.
                commands = [{"$type": "add_scene",
                             "name": a_and_s.scene.name,
                             "url": a_and_s.scene.get_url()},
                            {"$type": "add_humanoid_animation",
                             "name": a_and_s.animation.name,
                             "url": a_and_s.animation.get_url()},
                            {"$type": "create_avatar",
                             "type": "A_Img_Caps_Kinematic",
                             "id": "a"},
                            {"$type": "add_humanoid",
                             "name": humanoid.name,
                             "url": humanoid.get_url(),
                             "position": a_and_s.position,
                             "rotation": a_and_s.rotation,
                             "id": h_id},
                            {"$type": "set_pass_masks",
                             "pass_masks": ["_img"]}]
                if add_skybox:
                    commands.extend([self.get_add_hdri_skybox(skybox.name),
                                     {"$type": "set_post_exposure",
                                      "post_exposure": 0.4},
                                     {"$type": "set_aperture",
                                      "aperture": 1.6},
                                     {"$type": "set_contrast",
                                      "contrast": -20}])
                else:
                    # Set default post-processing values.
                    commands.extend([{"$type": "set_post_exposure"},
                                     {"$type": "set_aperture"},
                                     {"$type": "set_contrast"}])
                commands.extend(per_frame_commands)
                self.communicate(commands)

                frame = 0
                for loop in range(num_loops):
                    # Start to play the animation.
                    # Try to get all of the humanoid in the viewport.
                    init_loop_commands = per_frame_commands[:-1]
                    init_loop_commands.extend([{"$type": "play_humanoid_animation",
                                                "name": a_and_s.animation.name,
                                                "id": h_id}])
                    self.communicate(init_loop_commands)

                    if loop == 0:
                        resp = self.communicate({"$type": "send_humanoids",
                                                 "frequency": "once",
                                                 "ids": [h_id]})
                        tr = Transforms(resp[0])
                        o_pos = tr.get_position(0)
                        # Camera distance from the humanoid.
                        avatar_d = HumanoidVideo.RNG.uniform(-2.2, -4.5)
                        # A reasonable rotation.
                        avatar_theta = np.radians(HumanoidVideo.RNG.uniform(-85, 85))
                        # Get the avatar position from the angle and distance.
                        avatar_x = o_pos[0] + (avatar_d * np.cos(avatar_theta))
                        avatar_z = o_pos[2] + (avatar_d * np.sin(avatar_theta))
                        avatar_y = HumanoidVideo.RNG.uniform(1.8, 2 + (avatar_d * 0.12))
                        per_frame_commands.append({"$type": "teleport_avatar_to",
                                                   "position": {"x": avatar_x, "y": avatar_y, "z": avatar_z}})
                    # Play the animation.
                    count = 0
                    while count < a_and_s.animation.get_num_frames():
                        # Drop frames to stay at 30 FPS.
                        if count % save_per == 0:
                            resp = self.communicate(per_frame_commands)
                            TDWUtils.save_images(Images(resp[0]), TDWUtils.zero_padding(frame), output_dir,
                                                 append_pass=False)
                            frame += 1
                        else:
                            self.communicate([])
                        count += 1

                # Destroy the humanoid.
                self.communicate({"$type": "destroy_humanoid",
                                  "id": h_id})

                # Write the metadata file (signalling that the video was completed).
                metadata_path.write_text(json.dumps(metadata, indent=4), encoding="utf-8")

                if pbar is not None:
                    pbar.update(1)

    def run(self, num_camera_iterations: int = 1) -> None:
        """
        Create a target number of videos. In each video, choose a random humanoid, animation, scene, and skybox.

        :param num_camera_iterations: Make this many videos of each specific animation/humanoid/scene/skybox combo, changing the camera angle each time.
        """

        humanoids = HumanoidLibrarian().records
        skyboxes = HDRISkyboxLibrarian().records

        # Filter out interior and low-light skyboxes.
        skyboxes = [r for r in skyboxes if r.name != "sky_white" and r.location == "exterior" and
                    r.sun_intensity >= 1 and r.sun_elevation >= 145]

        num_videos = len(humanoids) * num_camera_iterations * len(self.animations_and_scenes)

        pbar = tqdm(total=num_videos)

        for animation_and_scene in self.animations_and_scenes:
            self.get_video(animation_and_scene, humanoids, skyboxes, pbar=pbar,
                           num_camera_iterations=num_camera_iterations)
        self.communicate({"$type": "terminate"})

    @staticmethod
    def _increment_record_count(index: int, records: list) -> int:
        """
        Iterate an index through a list.

        :param index: The current index in the list of records.
        :param records: The list of records.
        """

        index += 1
        if index >= len(records):
            index = 0
        return index


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--dir", type=str, default="D:/humanoid_video_output", help="Output directory")
    args = parser.parse_args()
    HumanoidVideo(Path(args.dir)).run()
