from pathlib import Path
from platform import system


ASSET_BUNDLE_VERIFIER_OUTPUT_DIR = Path.home().joinpath("tdw_asset_bundle_verifier")
EXAMPLE_CONTROLLER_OUTPUT_PATH = Path.home().joinpath("tdw_example_controller_output")

if system() == "Windows":
    PLAYER_LOG_PATH = Path.home().joinpath("AppData/LocalLow/MIT/TDW/Player.log")
    EDITOR_LOG_PATH = Path.home().joinpath("AppData/Local/Unity/Editor/Editor.log")
elif system() == "Darwin":
    PLAYER_LOG_PATH = Path.home().joinpath("Library/Logs/MIT/TDW/Player.log")
    EDITOR_LOG_PATH = Path.home().joinpath("Library/Logs/Unity/Editor.log")
else:
    assert system() == "Linux", f"Platform not supported: {system()}"
    PLAYER_LOG_PATH = Path.home().joinpath(".config/unity3d/MIT/TDW/Player.log")
    EDITOR_LOG_PATH = Path.home().joinpath(".config/unity3d/Editor.log")
