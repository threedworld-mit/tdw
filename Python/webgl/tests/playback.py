from pathlib import Path
from typing import List, Optional
import io
import numpy as np
from PIL import Image, ImageChops
from tdw.controller import Controller
from tdw.output_data import OutputData, Images, SystemInfo
from tdw.tdw_utils import TDWUtils
from tdw.webgl import TrialController, TrialMessage, TrialPlayback, END_MESSAGE, run
from tdw.webgl.trials.tests.output_data_benchmark import OutputDataBenchmark
from tdw.webgl.trial_adders import AtEnd


class PlaybackWriter(TrialController):
    """
    Compare physics-driven simulation data to saved non-physics data.
    """

    def __init__(self):
        self.playback: Optional[TrialPlayback] = None
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[OutputDataBenchmark(image_capture=True,
                                                        num_frames=100)],
                            adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        self.playback = playback
        return END_MESSAGE

    @classmethod
    def _get_max_size(cls) -> int:
        return 167772160


class PlaybackReader(Controller):
    def __init__(self, playback: TrialPlayback, path: str,
                 port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.path: Path = Path(path).resolve()
        self.playback: TrialPlayback = playback
        self.add_ons.append(self.playback)
        self.webgl_images: List[Image.Image] = list()
        # Store image data.
        for i in range(len(playback.frames)):
            for j in range(len(playback.frames[i])):
                r_id = OutputData.get_data_type_id(playback.frames[i][j])
                if r_id == "imag":
                    self.webgl_images.append(TDWUtils.get_pil_image(Images(playback.frames[i][j]), 0))
        self.diffs: List[float] = list()

    def run(self) -> None:
        for i in range(len(self.playback.frames)):
            # Initialize.
            if i < 3:
                self.communicate([])
            else:
                if i == 3:
                    # Start image capture.
                    resp = self.communicate([{"$type": "set_pass_masks",
                                              "pass_masks": ["_mask"]},
                                             {"$type": "send_images",
                                              "frequency": "always"}])
                else:
                    resp = self.communicate([])
                self.compare_images(webgl_frame=i, resp=resp)
        # End the simulation.
        self.communicate({"$type": "terminate"})
        difference = sum(self.diffs) / len(self.diffs)
        print("Average per-pixel discrepancy:", difference)
        # Create the output row.
        row = ""
        # Get system info.
        resp = self.playback.frames[0]
        for i in range(len(resp) - 1):
            r_id = SystemInfo.get_data_type_id(resp[i])
            if r_id == "syst":
                system_info = SystemInfo(resp[i])
                row += (f"{system_info.get_os()},{system_info.get_browser()},"
                        f"{system_info.get_gpu()},{system_info.get_graphics_api()},{difference}")
                break
        # Write the results to disk.
        with io.open(str(self.path), "at") as f:
            f.write("\n" + row)

    def compare_images(self, webgl_frame: int, resp: List[bytes]) -> None:
        """
        Parse `resp` and compare it to an image captured within WebGL.

        :param webgl_frame: The index of the WebGL frame. This is used to find the WebGL image.
        :param resp: The response from the build. This contains the Standalone image.
        """

        # Get image data captured by the standalone controller.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imag":
                # Get the standalone image.
                standalone_image = TDWUtils.get_pil_image(Images(resp[i]), 0)
                # Get the WebGL image.
                webgl_image = self.webgl_images[webgl_frame]
                # Diff the images.
                diff = ImageChops.difference(standalone_image, webgl_image)
                # Return the average diff.
                self.diffs.append(float(np.sum(np.array(diff)) / (255 * diff.size[0] * diff.size[1])))
                break


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--path", type=str, default="D:/tdw_docs/docs/webgl/tests/playback.csv")
    args, unknown = parser.parse_known_args()

    # Run the TrialController.
    tc = PlaybackWriter()
    run(tc)

    # Run the Standalone controller.
    c = PlaybackReader(playback=tc.playback, path=args.playback_table_path)
    c.run()
