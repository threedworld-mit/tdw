import h5py
import json
from typing import List
from random import uniform, random
from argparse import ArgumentParser
import numpy as np
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw_physics.rigidbodies_dataset import RigidbodiesDataset
from sticky_mitten_avatar.avatars import Baby


class VarianceAvatar(RigidbodiesDataset):
    """
    Test physics variances with an avatar in the scene.

    The controller creates stacks of boxes and then an avatar moves through the boxes.
    The avatar's movements are random but pre-calculated. See: VarianceAvatar.precalculate_commands
    This means that the movements are the same for every trial and test.
    The avatar movements are very sudden. This is intentional, as it should put stress on the physics engine.

    Requires: tdw_physics, sticky_mitten_avatar
    """

    FRAME_PATH = Path("frames.json")

    def __init__(self, port: int = 1071, launch_build: bool = True):
        super().__init__(port=port, launch_build=launch_build)
        self.cube = ModelLibrarian("models_flex.json").get_record("cube")

    def get_field_of_view(self) -> float:
        return 30

    def get_scene_initialization_commands(self) -> List[dict]:
        return [{"$type": "load_scene",
                 "scene_name": "ProcGenScene"},
                TDWUtils.create_empty_room(20, 20)]

    def get_per_frame_commands(self, resp: List[bytes], frame: int) -> List[dict]:
        return frames[frame]

    def is_done(self, resp: List[bytes], frame: int) -> bool:
        return frame == len(frames) - 1

    def get_trial_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "destroy_avatar"}]

        # Add a grid of cubes.
        d_y = 0.7
        d_x = 2
        d_z = 2
        o_id = 0
        for x in range(5):
            for y in range(10):
                for z in range(5):
                    if x == 0 and z == 0:
                        continue
                    commands.extend(self.add_physics_object(position={"x": x - d_x, "y": y * d_y, "z": z - d_z},
                                                            rotation=TDWUtils.VECTOR3_ZERO,
                                                            dynamic_friction=0.1,
                                                            static_friction=0.1,
                                                            bounciness=0.9,
                                                            o_id=o_id,
                                                            mass=2,
                                                            record=self.cube))
                    commands.extend([{"$type": "scale_object",
                                      "id": o_id,
                                      "scale_factor": {"x": 0.7, "y": 0.7, "z": 0.7}},
                                     {"$type": "set_object_collision_detection_mode",
                                      "id": o_id,
                                      "mode": detection_mode}])
                    o_id += 1
        commands.extend(TDWUtils.create_avatar(avatar_type="A_StickyMitten_Adult"))
        # Make the mittens sticky.
        for is_left in [True, False]:
            for side in ["palm", "back", "side"]:
                commands.append({"$type": "set_stickiness",
                                 "sub_mitten": side,
                                 "sticky": True,
                                 "is_left": is_left,
                                 "show": False})
        commands.extend([{"$type": "set_pass_masks",
                          "pass_masks": []},
                         {"$type": "send_images",
                          "frequency": "never"},
                         {"$type": "set_avatar_collision_detection_mode",
                          "mode": detection_mode}])
        return commands

    @staticmethod
    def precalculate_movements() -> None:
        """
        Precalculate random movements for the avatar before running this test.
        This way the movements are "random" per frame but the same per trial.
        """

        frames: List[List[dict]] = list()
        for i in range(num_frames):
            # Move and turn randomly.
            commands = [{"$type": "move_avatar_forward_by",
                         "magnitude": uniform(50, 100)},
                        {"$type": "rotate_avatar_by",
                         "angle": uniform(-45, 45),
                         "axis": "yaw",
                         "is_world": True,
                         "avatar_id": "a"}]
            # Bend arm joints randomly.
            for j in Baby.JOINTS:
                commands.append({"$type": "bend_arm_joint_by",
                                 "angle": uniform(0, 89),
                                 "joint": j.joint,
                                 "axis": j.axis})
            for is_left in [True, False]:
                if random() > 0.5:
                    commands.append({"$type": "pick_up_proximity",
                                     "distance": 3,
                                     "grip": 1000,
                                     "is_left": is_left})
                else:
                    commands.append({"$type": "put_down",
                                     "is_left": is_left})

            frames.append(commands)
        movements = {"id": Controller.get_unique_id(),
                     "frames": frames}
        VarianceAvatar.FRAME_PATH.write_text(json.dumps(movements))

    @staticmethod
    def get_variance():
        """
        Calculate the physics variance between trials.

        :return: A float representing the total variance.
        """

        # Get the positions of each object on the last frame.
        num_objects = 240
        trials = np.empty([num_trials, num_objects, 3])
        p = Path(d)
        for trial in p.glob("*.hdf5"):
            f = h5py.File(str(trial.resolve()), "r")
            # Get the last frame.
            frame_key = list(f["frames"].keys())[-1]
            object_ids = f["static"]["object_ids"]
            # Record the position of each object.
            frame_positions = np.array(f["frames"][frame_key]["objects"]["positions"])
            for i in range(len(frame_positions)):
                trials[int(trial.stem)][object_ids[i]] = frame_positions[i]
        variance = np.mean(np.var(trials, axis=0))
        p.joinpath("variance.txt").write_text(str(variance))
        return variance


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--num_trials", type=int, default=10, help="Number of trials")
    parser.add_argument("--num_frames", type=int, default=300, help="Number of frames")
    parser.add_argument("--precalculate", action="store_true", help="Precalculate movements")
    args = parser.parse_args()
    num_trials = args.num_trials
    num_frames = args.num_frames

    if args.precalculate:
        VarianceAvatar.precalculate_movements()
        exit()
    # Get the cached random movements.
    frame_data = json.loads(Path("frames.json").read_text())
    frame_id = frame_data["id"]
    frames = frame_data["frames"]
    # Test each detection mode.
    table = "| Detection Mode | Variance |\n| --- | --- |\n"
    for detection_mode in ["continuous", "continuous_speculative", "continuous_dynamic", "discrete"]:
        d = f"D:/avatar_variance/{frame_id}_{detection_mode}"
        temp_path = Path("D:/temp")

        c = VarianceAvatar()
        c.run(num=num_trials, output_dir=d, temp_path="D:/temp", width=128, height=128)
        # Stop the controller.
        c.socket.close()
        table += f"| {detection_mode} | {VarianceAvatar.get_variance()} |\n"
    print(table)
