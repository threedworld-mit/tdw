from pathlib import Path
import io
from tdw.output_data import OutputData, TimeSinceStartup, SystemInfo
from tdw.webgl import TrialController, TrialMessage, TrialPlayback, END_MESSAGE, run
from tdw.webgl.trials.tests.load_time import LoadTime as LoadTimeTrial
from tdw.webgl.trial_adders import AtEnd


class LoadTime(TrialController):
    def __init__(self, path: str):
        self.path: Path = Path(path).resolve()
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[LoadTimeTrial()],
                            adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        got_startup_time = False
        row = ""
        for i in range(len(playback.frames)):
            for j in range(len(playback.frames[i])):
                r_id = OutputData.get_data_type_id(playback.frames[i][j])
                # Get system info.
                if r_id == "syst":
                    system_info = SystemInfo(playback.frames[i][j])
                    row += (f"{system_info.get_os()},{system_info.get_browser()},"
                            f"{system_info.get_gpu()},{system_info.get_graphics_api()},")
                # Get the time since startup.
                elif r_id == "tsst":
                    row += str(TimeSinceStartup(playback.frames[i][j]).get_ticks() / 10000000)
                    # Append the row.
                    with io.open(self.path, "at") as f:
                        f.write("\n" + row)
                    got_startup_time = True
                    break
            if got_startup_time:
                break
        return END_MESSAGE


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--path", type=str, default="D:/tdw_docs/docs/webgl/tests/load_time.csv")
    args, unknown = parser.parse_known_args()

    run(LoadTime(path=args.path))
