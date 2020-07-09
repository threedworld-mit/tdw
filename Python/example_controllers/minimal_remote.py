import argparse
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
A minimal example of how to use the launch binaries daemon to
start and connect to a build on a remote node. Note: the remote
must be running launch_binaries.py.
"""


class MinimalRemote(Controller):
    def __init__(self,
                 listener_port="5556",
                 build_address="node14-ccncluster.stanford.edu",
                 controller_address="node05-ccncluster.stanford.edu"):

        args = self.parse_args()
        build_info = TDWUtils.launch_build(args.listening_port,
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
        # Start the controller.
        self.start()

        # Create an empty environment.
        # Tell the build to send "junk" data per frame.
        self.communicate([{"$type": "create_empty_environment"},
                          {"$type": "send_junk",
                           "frequency": "always",
                           "length": 1}
                          ])

        for i in range(100):
            # Do nothing. Receive a response from the build.
            resp = self.communicate({"$type": "do_nothing"})

            # Print the frame and the data.

            print(f"Frame {self.get_frame(resp[-1])}\t{resp[0]}")


if __name__ == "__main__":
    MinimalRemote().run()
