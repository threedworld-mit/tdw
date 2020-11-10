from argparse import ArgumentParser
import numpy as np
from pathlib import Path
import h5py
from typing import List
from tdw.librarian import ModelLibrarian
from tdw.tdw_utils import TDWUtils
from tdw_physics.rigidbodies_dataset import RigidbodiesDataset


class Variance(RigidbodiesDataset):
    """
    Calculate the variance of physics trials.
    Each trial has the exact same setup.
    After the trials are done, calculate the variance of end positions (where each object is at the end of the trial)
    between multiple trials. Then, average those values for a single "variance" rating.
    This can be used to determine how deterministic the Unity Engine is.
    A lower "variance" means more determinism.

    This controller requires tdw_physics: https://github.com/alters-mit/tdw_physics
    """

    def __init__(self):
        self.record = ModelLibrarian("models_flex.json").get_record("cone")
        self.r = 7.0

        super().__init__()

    def get_scene_initialization_commands(self) -> List[dict]:
        # Load the proc-gen room.
        # Disable images.
        return [{"$type": "load_scene", "scene_name": "ProcGenScene"},
                TDWUtils.create_empty_room(100, 100)]

    def get_trial_initialization_commands(self) -> List[dict]:
        # Initialize the exact same trial every time.
        commands = [{"$type": "set_pass_masks",
                     "pass_masks": []},
                    {"$type": "send_images",
                     "frequency": "never"}]

        # Drop a circle of cubes.
        for i in range(145):
            # Add an object.
            commands.extend(self.add_physics_object(record=self.record,
                                                    mass=2.7,
                                                    position={"x": 0, "y": i, "z": 0},
                                                    rotation=TDWUtils.VECTOR3_ZERO,
                                                    dynamic_friction=0.1,
                                                    static_friction=0.1,
                                                    bounciness=0.9,
                                                    o_id=i))
            commands.append({"$type": "scale_object",
                             "id": i,
                             "scale_factor": {"x": 0.7, "y": 0.7, "z": 0.7}})
            commands.append({"$type": "set_object_collision_detection_mode",
                             "id": i,
                             "mode": detection_mode})
        return commands

    def get_per_frame_commands(self, resp: List[bytes], frame: int) -> List[dict]:
        return []

    def get_field_of_view(self) -> float:
        return 30

    def is_done(self, resp: List[bytes], frame: int) -> bool:
        return frame >= 300

    @staticmethod
    def get_variance(uv: str):
        """
        Calculate the physics variance between trials.

        :param uv: The Unity version.

        :return: A float representing the total variance.
        """

        print("Calculating variance... (this will take a minute)")
        p = Path(f"D:/variance_{uv}_{detection_mode}")

        # Get the positions of each object on the last frame.
        num_objects = 145
        trials = np.empty([num_trials, num_objects, 3])
        for trial in p.glob("*.hdf5"):
            f = h5py.File(str(trial.resolve()), "r")
            # Get the last frame.
            frame_key = list(f["frames"].keys())[-1]
            object_ids = f["static"]["object_ids"]
            # Record the position of each object.
            frame_positions = np.array(f["frames"][frame_key]["objects"]["positions"])
            for i in range(len(frame_positions)):
                trials[int(trial.stem)][object_ids[i]] = frame_positions[i]
        # trials = trials.reshape((num_trials, -1))
        variance = np.mean(np.var(trials, axis=0))
        p.joinpath("variance.txt").write_text(str(variance))
        return variance


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--coll_mode", type=str, default="continuous_dynamic", help="Collision detection mode",
                        choices=["continuous", "continuous_speculative", "discrete", "continuous_dynamic"])
    parser.add_argument("--num_trials", type=int, default=10, help="Number of trials")
    args = parser.parse_args()
    detection_mode = args.coll_mode
    num_trials = args.num_trials

    c = Variance()
    # Use the Unity version to name the output directory.
    tdw_version, unity_version = c.get_version()
    unity_version = unity_version.split(" ")[-1]
    d = f"D:/variance_{unity_version}_{detection_mode}"

    # Run the trials.
    c.run(num=num_trials, output_dir=d, temp_path="D:/temp", width=128, height=128)
    # Stop the controller.
    c.socket.close()

    print(Variance.get_variance(unity_version))
