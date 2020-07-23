from subprocess import Popen, PIPE, DEVNULL
import re


__version__ = "1.6.1"
last_stable_release = "1.6.0"


def strip_post_release(v: str) -> str:
    """
    If the version number has a post-release suffix (a fourth number), strip it.

    :param v: The version number.

    :return: The version, stripped of the post-release suffix.
    """

    if len(v.split(".")) >= 3:
        # Get the post-release suffix and then return a sliced string using its length.
        return v[:-len(re.search(r"(?:.(?!\.))+$", v).group(0))]
    else:
        return v


def get_pypi_version(truncate: bool = False) -> str:
    """
    :param truncate: If true, remove the post-release number (the fourth number) if there is one.

    :return: The newest available tdw release on PyPi.
    """

    # Get an error from  PyPi which will list all available versions.
    p = Popen(["pip3", "install", "tdw=="], stderr=PIPE, shell=True, stdout=DEVNULL).stderr.read().decode("utf-8")
    # From the list of available versions, get the last one (the most recent).
    v = re.search(r"\(from versions: (.*)\)", p).group(1).split(",")[-1].strip()

    # Strip the post-release suffix.
    if truncate:
        return strip_post_release(v)
    else:
        return v


def get_installed_tdw_version(truncate: bool = False) -> str:
    """
    :param truncate: If true, remove the post-release number (the fourth number) if there is one.

    :return: The version of the tdw Python module installed on this machine.
    """

    # Get info on the tdw module.
    p = Popen(["pip3", "show", "tdw"], shell=True, stdout=PIPE).stdout.read().decode("utf-8")
    # Get the version from the output.
    v = re.search(r"Version: (.*)", p, flags=re.MULTILINE).group(1)

    # Strip the post-release suffix.
    if truncate:
        return strip_post_release(v)
    else:
        return v
