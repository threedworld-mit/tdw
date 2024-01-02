from pathlib import Path
from tdw.webgl import END_MESSAGE, TrialController, TrialMessage, TrialPlayback
from tdw.webgl.trials.test_scene import TestScene as TestSceneTrial
from tdw.webgl.trial_adders.at_end import AtEnd
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class TestScene(TrialController):
    """
    Run a single `TestScene` trial.
    """

    def __init__(self):
        self._path: Path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("webgl_test_scene/playback.gz").resolve()
        print(f"Data will be saved to: {self._path}")
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True)
        super().__init__()

    def get_initial_message(self) -> TrialMessage:
        return TrialMessage(trials=[TestSceneTrial()], adder=AtEnd())

    def get_next_message(self, playback: TrialPlayback) -> TrialMessage:
        return END_MESSAGE

    def _on_receive(self, bs: bytes) -> None:
        # Write to disk.
        self._path.write_bytes(bs)


if __name__ == "__main__":
    from tdw.webgl import run
    run(TestScene())
