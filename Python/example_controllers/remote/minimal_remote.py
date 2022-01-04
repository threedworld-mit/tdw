import argparse
from tdw.controller import Controller
from tdw.remote_build_launcher import RemoteBuildLauncher


class MinimalRemote(Controller):
    """
    A minimal example of how to use the launch binaries daemon to
    start and connect to a build on a remote node. Note: the remote
    must be running binary_manager.py.
    """

    def __init__(self):
        args = self.parse_args()
        build_info = RemoteBuildLauncher.launch_build(args.listening_port,
                                                      args.build_address,
                                                      args.controller_address)

        super().__init__(port=build_info["build_port"])

    def parse_args(self):
        """
        Helper function that parses command line arguments .
        Returns parsed args.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--listening_port",
            default="5556",
            type=str,
            help="Port on which binary_manager is listening",
        )
        parser.add_argument(
            "--build_address",
            default="node14-ccncluster.stanford.edu",
            type=str,
            help="IP/hostname on which to launch build",
        )
        parser.add_argument(
            "--controller_address",
            default="node05-ccncluster.stanford.edu",
            type=str,
            help="Address of controller",
        )
        args = parser.parse_args()
        return args

    def run(self):
        # Create an empty environment.
        self.communicate({"$type": "create_empty_environment"})
        for i in range(100):
            # Do nothing. Receive a response from the build.
            resp = self.communicate([])
            print(resp)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    MinimalRemote().run()
