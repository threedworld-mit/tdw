from pathlib import Path
from platform import system
from tdw.backend.platforms import SYSTEM_TO_EXECUTABLE


BUILD_ROOT_DIR = Path.home().joinpath(f"tdw_build")
BUILD_PATH = BUILD_ROOT_DIR.joinpath(f"TDW/TDW{SYSTEM_TO_EXECUTABLE[system()]}")
ASSET_BUNDLE_VERIFIER_OUTPUT_DIR = Path.home().joinpath("tdw_asset_bundle_verifier")
VALIDATOR_REPORT_PATH = ASSET_BUNDLE_VERIFIER_OUTPUT_DIR.joinpath("validator_report.json")

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
