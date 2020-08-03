from requests import get, head
from typing import Tuple
from platform import system
from pathlib import Path
from zipfile import ZipFile
from distutils import dir_util
from subprocess import call, check_output, Popen
from tdw.version import __version__
import docker
from tdw.backend.platforms import SYSTEM_TO_RELEASE, SYSTEM_TO_EXECUTABLE


class Docker:
    """
    Check the Docker version and update the image as needed.
    """

    @staticmethod
    def get_local_tag() -> str:
        """
        Returns the tag of the local Docker image.
        """

        return [x for x in check_output(["docker", "images", "tdw"]).decode('utf-8').split("\n")[1].split(" ") if
                x != ""][1]

    @staticmethod
    def pull() -> None:
        """
        Pull a Docker image corresponding to the installed version of TDW.
        """

        call(["docker", "pull", f"tdw:{__version__}"])

    @staticmethod
    def run(display: int) -> None:
        """
        Run a build of TDW in a Docker container.

        :param display: If launch_build == True, launch the build using this display number (Linux-only).
        """

        Popen(["docker", "run", "-it",
               "--rm",
               "--gpus", "all",
               "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
               "-e", f"DISPLAY=:{display}",
               "--network", "host",
               f"tdw:{__version__}",
               "./TDW/TDW.x86_64"],
              shell=False)

    @staticmethod
    def stop() -> None:
        """
        Stop the container.
        """

        call(["docker", "stop", "tdw"])
