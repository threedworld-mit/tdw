from typing import Optional
from pathlib import Path
import io
from datetime import datetime
from gzip import GzipFile
from statistics import stdev
from tdw.type_aliases import PATH
from tdw.tdw_utils import TDWUtils
from tdw.output_data import SystemInfo
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback, run
from tdw.webgl.trials.tests.output_data_benchmark import OutputDataBenchmark
from tdw.webgl.trial_adders.at_end import AtEnd


class OutputData(TrialController):
    """
    Output data benchmark.
    """

    def __init__(self, output_directory: PATH = None, benchmark_table_path: PATH = None):
        self.compressed_size: float = -1
        self.uncompressed_size: float = -1
        self.output_directory: Optional[Path] = TDWUtils.get_path(output_directory) if output_directory is not None else None
        if self.output_directory is not None and not self.output_directory.exists():
            self.output_directory.mkdir(parents=True)
        self.benchmark_table_path: Optional[str] = TDWUtils.get_string_path(benchmark_table_path) if benchmark_table_path is not None else None
        self.filename: str = str(datetime.utcnow().strftime("%m%d%Y_%H%M%S")) + ".gz"
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[OutputDataBenchmark()], adder=AtEnd())

    def _on_receive(self, bs: bytes) -> None:
        self.compressed_size = TDWUtils.bytes_to_megabytes(len(bs))
        f = io.BytesIO(bs)
        with GzipFile(fileobj=f, mode="rb") as gz:
            buffer: bytes = gz.read()
        self.uncompressed_size = TDWUtils.bytes_to_megabytes(len(buffer))
        print("WebGL Benchmark:")
        print("Data size (MB):", self.compressed_size)
        print("Uncompressed size (MB):", self.uncompressed_size)
        # Write to disk.
        if self.output_directory is not None:
            path = self.output_directory.joinpath(self.filename)
            path.write_bytes(bs)

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        fps = playback.get_fps()
        print("FPS:", fps)
        if self.benchmark_table_path is not None:
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
                    row += (f"{self.filename},{system_info.get_os()},{system_info.get_browser()},{system_info.get_cpu()},"
                            f"{system_info.get_gpu()},{system_info.get_graphics_api()},{fps},{dt_stdev}")
            # Append the row.
            with io.open(self.benchmark_table_path, "at") as f:
                f.write("\n" + row)
        return END_MESSAGE


if __name__ == "__main__":
    from argparse import ArgumentParser

    default_output_path = Path("D:/tdw_docs/docs/webgl/benchmarks/output_data").resolve()
    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--output_directory", type=str, default=str(default_output_path))
    parser.add_argument("--benchmark_table_path", type=str, default=str(default_output_path.joinpath("output_data.csv")))
    args, unknown = parser.parse_known_args()
    run(OutputData(output_directory=args.output_directory, benchmark_table_path=args.benchmark_table_path))
