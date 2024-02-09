from tdw.webgl.trial_playback import TrialPlayback
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

playback = TrialPlayback()
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("photodiode_test/output.gz").resolve()
playback.load(path)
for _ , timestamp in zip(playback.frames, playback.timestamps):
    print(timestamp)
fps = playback.get_fps()
print("FPS = " + str(fps))