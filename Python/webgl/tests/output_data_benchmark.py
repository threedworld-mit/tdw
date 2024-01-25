import io
from statistics import stdev
from tdw.output_data import SystemInfo
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback, run
from tdw.webgl.trials.tests.output_data_benchmark import OutputDataBenchmark as OutputDataBenchmarkTrial
from tdw.webgl.trial_adders.at_end import AtEnd


class OutputDataBenchmark(TrialController):
    """
    Output data benchmark.
    """

    def __init__(self, path: str):
        self.path: str = path
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[OutputDataBenchmarkTrial()],
                            adder=AtEnd(),
                            send_data_per_frame=self._send_per_frame())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        fps = playback.get_fps()
        print("FPS:", fps)
        # Get the variance between frames.
        dt_stdev = stdev(playback.get_time_deltas())
        # Start a csv row.
        row = ""
        # Get system info.
        resp = playback.frames[0]
        for i in range(len(resp) - 1):
            r_id = SystemInfo.get_data_type_id(resp[i])
            if r_id == "syst":
                system_info = SystemInfo(resp[i])
                row += (f'"{system_info.get_os()}","{system_info.get_browser()}",'
                        f'"{system_info.get_gpu()}","{system_info.get_graphics_api()}",{fps},{dt_stdev}')
        # Append the row.
        with io.open(self.path, "at") as f:
            f.write("\n" + row)
        return END_MESSAGE

    @classmethod
    def _send_per_frame(cls) -> bool:
        return False


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--path", type=str, default="D:/tdw_docs/docs/webgl/tests/output_data.csv")
    args, unknown = parser.parse_known_args()
    run(OutputDataBenchmark(path=args.path))
