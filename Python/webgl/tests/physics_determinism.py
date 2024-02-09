import io
from typing import Optional
from pathlib import Path
from argparse import ArgumentParser
import numpy as np
from tdw.output_data import OutputData, FastTransforms, SystemInfo, Version
from tdw.webgl import TrialController, TrialPlayback, TrialMessage, END_MESSAGE, run
from tdw.webgl.trial_adders import AtEnd
from tdw.webgl.trials.tests.physics_determinism import PhysicsDeterminism as PhysicsDeterminismTrial


class PhysicsDeterminism(TrialController):
    CANONICAL_FILENAME: str = "canon.gz"

    def __init__(self, path: str, canon: bool):
        self.path: Path = Path(path).resolve()
        if not self.path.exists():
            self.path.mkdir(parents=True)
        self.canon: bool = canon
        # If we're creating the canonical playback, we don't need to load data.
        if self.canon:
            self.canonical_positions: Optional[np.ndarray] = None
            self.canonical_rotations: Optional[np.ndarray] = None
        # Load the canonical file and store its data.
        else:
            playback = TrialPlayback()
            playback.load(self.path.joinpath(PhysicsDeterminism.CANONICAL_FILENAME))
            positions = list()
            rotations = list()
            # Iterate through each frame.
            for resp in playback.frames:
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    # Append FastTransforms data.
                    if r_id == "ftra":
                        fast_transforms = FastTransforms(resp[i])
                        positions.append(fast_transforms._positions)
                        rotations.append(fast_transforms._rotations)
            self.canonical_positions = np.array(positions)
            self.canonical_rotations = np.array(rotations)
        self.frame: int = 0
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[PhysicsDeterminismTrial()], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        # Save the physics determinism value.
        if not self.canon:
            # Set the positions and rotations arrays.
            positions = np.zeros(shape=self.canonical_positions.shape)
            rotations = np.zeros(shape=self.canonical_rotations.shape)
            for i in range(len(playback.frames) - 1):
                resp = playback.frames[i]
                for j in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[j])
                    # Get FastTransforms data.
                    if r_id == "ftra":
                        fast_transforms = FastTransforms(resp[j])
                        # Store the positions and rotations of this frame.
                        positions[self.frame] = fast_transforms._positions
                        rotations[self.frame] = fast_transforms._rotations
                        self.frame += 1
            # Flatten the arrays and get the difference.
            position_difference = np.linalg.norm(self.canonical_positions.flatten() - positions.flatten())
            rotation_difference = np.linalg.norm(self.canonical_rotations.flatten() - rotations.flatten())
            row = ""
            # Get system info.
            resp = playback.frames[0]
            for i in range(len(resp) - 1):
                r_id = SystemInfo.get_data_type_id(resp[i])
                if r_id == "vers":
                    version = Version(resp[i])
                    row += f'"{version.get_standalone()}",'
                if r_id == "syst":
                    system_info = SystemInfo(resp[i])
                    row += (f'"{system_info.get_os()}","{system_info.get_browser()}",'
                            f'"{system_info.get_gpu()}","{system_info.get_graphics_api()}",'
                            f'{position_difference},{rotation_difference}')
            # Append the row.
            with io.open(str(self.path.joinpath("physics_determinism.csv")), "at") as f:
                f.write("\n" + row)
        return END_MESSAGE

    def on_receive_trial_end(self, bs: bytes) -> None:
        # Set the filename to the canon name.
        if self.canon:
            self.path.joinpath(PhysicsDeterminism.CANONICAL_FILENAME).write_bytes(bs)


if __name__ == "__main__":
    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--path", type=str, default="D:/tdw_docs/docs/webgl/tests/physics_determinism",
                        help="The path to the output folder.")
    parser.add_argument("--canon", action="store_true",
                        help="Write this data as the canonical data.")
    args, unknown = parser.parse_known_args()
    run(PhysicsDeterminism(path=args.path, canon=args.canon))
