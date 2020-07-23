from typing import Dict

# Convert platform.system() to S3 URL infixes.
SYSTEM_TO_S3: Dict[str, str] = {"Windows": "windows",
                                "Darwin": "osx",
                                "Linux": "linux"}
# Convert S3 URL infixes to Unity build targets.
S3_TO_UNITY: Dict[str, str] = {"windows": "StandaloneWindows64",
                               "osx": "StandaloneOSX",
                               "linux": "StandaloneLinux64"}
# Convert platform.system() to Unity build targets.
SYSTEM_TO_UNITY: Dict[str, str] = {"Windows": "StandaloneWindows64",
                                   "Darwin": "StandaloneOSX",
                                   "Linux": "StandaloneLinux64"}
# Convert Unity build targets to platform.system()
UNITY_TO_SYSTEM: Dict[str, str] = {"StandaloneWindows64": "Windows",
                                   "StandaloneOSX": "Darwin",
                                   "StandaloneLinux64": "Linux"}

# Convert the system platform to the build's executable extension.
SYSTEM_TO_EXECUTABLE: Dict[str, str] = {"Windows": ".exe",
                                        "Darwin": ".app",
                                        "Linux": ".x86_64"}

# Convert the system platform to the name of the zipped release file on GitHub.
SYSTEM_TO_RELEASE: Dict[str, str] = {"Windows": "TDW_Windows",
                                     "Darwin": "TDW_OSX",
                                     "Linux": "TDW_Linux"}
