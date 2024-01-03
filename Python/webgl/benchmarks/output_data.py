from io import BytesIO
from gzip import GzipFile
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback, run
from tdw.webgl.trials.tests.output_data_benchmark import OutputDataBenchmark
from tdw.webgl.trial_adders.at_end import AtEnd
from tdw.tdw_utils import TDWUtils


class OutputData(TrialController):
    """
    Output data benchmark.
    """

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[OutputDataBenchmark()], adder=AtEnd())

    def _on_receive(self, bs: bytes) -> None:
        print("WebGL Benchmark:")
        print("Data size (MB):", TDWUtils.bytes_to_megabytes(len(bs)))
        f = BytesIO(bs)
        with GzipFile(fileobj=f, mode="rb") as gz:
            buffer: bytes = gz.read()
        print("Uncompressed size (MB):", TDWUtils.bytes_to_megabytes(len(buffer)))
        print("")

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        print("FPS:", playback.get_fps())
        return END_MESSAGE


if __name__ == "__main__":
    run(OutputData())
