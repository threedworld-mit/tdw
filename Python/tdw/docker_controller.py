from subprocess import call, check_output, Popen
from tdw.version import __version__
from tdw.controller import Controller


class DockerController(Controller):
    def __init__(self, display: int, port: int = 1071):
        super().__init__(port=port, display=display, launch_build=False)

        docker_tag = DockerController.get_local_tag()

        # Pull an image matching this version.
        if docker_tag == "" or docker_tag != __version__:
            DockerController.pull()

    @staticmethod
    def get_local_tag() -> str:
        """
        Returns the tag of the local Docker image.
        """

        table = check_output(["docker", "images", "tdw"]).decode('utf-8').split("\n")
        if len(table) < 2:
            return ""
        table = [x for x in table[1].split(" ") if x != ""]
        if len(table) < 2:
            return ""
        return table[1]

    @staticmethod
    def pull() -> None:
        """
        Pull a Docker image corresponding to the installed version of TDW.
        """

        call(["docker", "pull", f"tdw:{__version__}"])

    @staticmethod
    def run_docker(display: int, *argv) -> None:
        """
        Run a build of TDW in a Docker container.

        :param display: If launch_build == True, launch the build using this display number (Linux-only).
        """

        cmd = ["docker", "run", "-e", f"DISPLAY=:{display}"]
        cmd.extend(argv)
        cmd.extend([f"tdw:{__version__}",
                    "./TDW/TDW.x86_64"])
        Popen(cmd, shell=False)

    @staticmethod
    def run_headless(display: int, *argv):
        """
        Run a headless instance of TDW in a Docker container.
        """

        args = ["-it",
                "--rm",
                "--gpus", "all",
                "-v", "/tmp/.X11-unix:/tmp/.X11-unix",
                "--network", "host"]
        args.extend(argv)

        DockerController.run_docker(display, args)

    @staticmethod
    def run_xpra(display: int):
        """
        Run the Docker container with xpra.
        """

        call([f"DISPLAY=:{display}"])
        call(["xhost", "+local:root"])
        call(["xpra", "start", ":80"])
        call(["DISPLAY=:80"])
        call(["xhost", "+local:root"])
        DockerController.run_headless(display, ["vglrun", "-d", f":{display}"])
