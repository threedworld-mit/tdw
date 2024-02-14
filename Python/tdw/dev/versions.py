from pathlib import Path
from typing import Dict, Tuple
from packaging import version
import re
from tdw.dev.config import Config


"""
The version numbers of the different components of TDW.
"""


__c = Config()
PROJECT_SETTINGS_PATH: Path = __c.tdwunity_path.joinpath("TDWUnity/ProjectSettings")

# The version in TDWUnity.
VERSION_TDWUNITY: str = re.search(r"bundleVersion: (.*)",
                                  PROJECT_SETTINGS_PATH.joinpath("ProjectSettings.asset").read_text(),
                                  flags=re.MULTILINE).group(1)

# The Unity Editor version.
VERSION_UNITY_EDITOR: str = re.search(r"m_EditorVersion: (.*)",
                                      PROJECT_SETTINGS_PATH.joinpath("ProjectVersion.txt").read_text(),
                                      flags=re.MULTILINE).group(1)

# The version in tdw.
VERSION_TDW: str = re.search(r"__version__ = \"(.*)\"",
                             __c.tdw_path.joinpath("Python/tdw/version.py").read_text(),
                             flags=re.MULTILINE).group(1)


def versions_are_equal() -> Tuple[bool, Dict[str, str]]:
    """
    :return: True if all version numbers (TDWUnity, tdw, and setup.py) are the same, and the versions themselves.
    """

    versions = {"TDWUnity": VERSION_TDWUNITY,
                "tdw": ".".join([str(q) for q in version.parse(VERSION_TDW).release[:-1]])}
    equal = len(set(versions.values())) == 1
    return equal, versions
