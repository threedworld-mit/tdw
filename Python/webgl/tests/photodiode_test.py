from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback, run
from tdw.webgl.trials.tests.output_data_benchmark import OutputDataBenchmark
from tdw.webgl.trial_adders import AtEnd
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class PhotodiodeTest(TrialController):
    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[OutputDataBenchmark(photodiode=True)], adder=AtEnd())
    
    def on_receive_trial_end(self, bs: bytes) -> None:
        # Write the end-of-trial data to disk.
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("photodiode_test/output.gz").resolve()
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        path.write_bytes(bs)

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE


if __name__ == "__main__":
    run(PhotodiodeTest())