from typing import Optional
from pathlib import Path
import io
from gzip import GzipFile
from tdw.type_aliases import PATH
from tdw.tdw_utils import TDWUtils
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback, run
from tdw.webgl.trials.tests.output_data_benchmark import OutputDataBenchmark as OutputDataBenchmarkTrial
from tdw.webgl.trial_adders.at_end import AtEnd


class Compression(TrialController):
    """
    Write the size of the compressed data sent from the build vs. the size of the uncompressed data.
    """

    def __init__(self, output_path: PATH):
        self.output_path: Optional[Path] = TDWUtils.get_path(output_path)
        if not self.output_path.parent.exists():
            self.output_path.mkdir(parents=True)
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[OutputDataBenchmarkTrial()], adder=AtEnd())

    def _on_receive(self, bs: bytes) -> None:
        cs = len(bs)
        f = io.BytesIO(bs)
        with GzipFile(fileobj=f, mode="rb") as gz:
            buffer: bytes = gz.read()
        us = len(buffer)
        self.output_path.write_text(f"compressed = {cs}\nuncompressed = {us}\nratio = {round(cs / us, 4)}")

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE


if __name__ == "__main__":
    from argparse import ArgumentParser

    default_output_path = Path("D:/tdw_docs/docs/webgl/tests/compression.txt").resolve()
    parser = ArgumentParser(allow_abbrev=False)
    parser.add_argument("--output_path", type=str, default=str(default_output_path))
    args, unknown = parser.parse_known_args()
    run(Compression(output_path=args.output_path))
