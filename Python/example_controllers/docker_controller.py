from tdw.release.docker import Docker
from tdw.controller import Controller


"""
This controller launches the build in a Docker container.
"""


class DockerController(Controller):
    def __init__(self, port: int = 1071, display: int = 0):
        super().__init__(port=port, launch_build=True, display=display, docker=True)

    def run(self):
        self.start()
        print("HERE")
        self.communicate({"$type": "terminate"})
        Docker.stop()


if __name__ == "__main__":
    DockerController().run()
