import zmq
import time
import argparse
import os
import itertools
import subprocess
import socket
import signal
from contextlib import closing
from threading import Thread


class BinaryManager:
    """
    Binary manager that launches TDW binaries for use with remote and local controllers.

    Usage: python3 binary_manager.py
    """
    @staticmethod
    def _format_args_unity(arg_dict):
        """
        Takes in a dictionary of key, value pairs and formats the arguments.
        Returns the formatted command line string that is accepted by unity arg parser.

        :param arg_dict: The dictionary of key, value pairs.
        """
        formatted_args = []
        for key, value in arg_dict.items():
            prefix = "-" + key + "="
            if type(value) == list:
                prefix += ",".join([str(v) for v in value])
            else:
                prefix += str(value)
            formatted_args += [prefix]
        return formatted_args

    @staticmethod
    def _find_free_port():
        """
        Returns a free port as a string.
        """
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(("", 0))
            return int(s.getsockname()[1])

    def _start_binary(self, message, args):
        """
        Starts the TDW binary.
        Returns a dictionary containing information about the binary instance.

        :param message: The message dict from controller with binary start request.
        :param args: The args defined upon initializing this script defining binary.
        """
        controller_address = message["controller_address"]
        build_port = self._find_free_port()
        gpu_id = next(args.gpus)
        os.environ["DISPLAY"] = ":0." + str(gpu_id)
        build_args = self._format_args_unity(
            {
                "screenHeight": str(args.screen_height),
                "screenWidth": str(args.screen_width),
                "address": controller_address,
                "port": build_port,
                "gpuDevice": gpu_id,
            }
        )
        if args.force_glcore42:
            build_args += ["-force-glcore42"]
        proc = subprocess.Popen([args.build_path] + build_args,
                                stdout=subprocess.PIPE)
        build_pid = proc.pid
        print("Starting build with pid: {} on port: {}".format(build_pid,
                                                               build_port))
        print(build_args)
        build_info = {
            "build_port": build_port,
            "build_pid": build_pid,
            "last_keep_alive": time.time(),
        }
        return build_info

    def _handle_message(self, message, args, socket, build_index):
        """
        Receives messages from the controller and calls the appropriate function.

        :param message: The message dict from controller.
        :param args: The args defined upon initializing this script defining binary.
        :param socket: The zmq socket from controller.
        :param build_index: The dict containing all active binaries.
        """
        if message["type"] == "start_build":
            build_info = self._start_binary(message, args)
            build_port = build_info["build_port"]
            build_index[build_port] = build_info
            socket.send_json(build_info)

        elif message["type"] == "keep_alive":
            build_port = message["build_port"]
            build_index[build_port]["last_keep_alive"] = time.time()
            socket.send_json(message)

        elif message["type"] == "kill_build":
            build_port = message["build_port"]
            pid = build_index[build_port]["build_pid"]
            os.kill(pid, signal.SIGKILL)
            socket.send_json({"type": "build_killed", "build_pid": pid})
            print("Killing build with pid: {} on port: {}".format(pid,
                                                                  build_port))

        else:
            socket.send_json({"type": "no_response"})

    @staticmethod
    def _garbage_collector(build_index):
        """
        Garbage collector that scans each active binary in build index
        and culls binaries that have been running for longer than 5 minutes
        without a keep alive signal.

        :param build_index: The dict containing all active binaries.
        """
        while True:
            current_time = time.time()
            builds_to_remove = []
            for build, build_info in build_index.items():
                if current_time - build_info["last_keep_alive"] > 300:
                    builds_to_remove.append(build)
                    build_pid = build_info["build_pid"]
                    build_port = build_info["build_port"]
                    os.kill(build_pid, signal.SIGKILL)
                    print("Killing build with pid: {} on port: {}".format(build_pid,
                                                                          build_port))

            for build in builds_to_remove:
                build_index.pop(build)

            time.sleep(60)

    def run(self, args):
        """
        Wrapper function that starts the launch binary event loop

        :param args: The args defined upon initializing this script defining binary.
        """
        port = args.listening_port
        build_index = dict()

        thread = Thread(target=self._garbage_collector, args=(build_index,))
        thread.start()

        context = zmq.Context()
        # noinspection PyUnresolvedReferences
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % port)
        while True:
            #  Wait for next request from client
            message = socket.recv_json()
            self._handle_message(message, args, socket, build_index)
            print("Received request: ", message)


def _get_binary_manager_args():
    """
    Helper function that parses command line arguments .
    Returns parsed args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--listening_port",
        default="5556",
        type=str,
        help="The socket port",
    )
    # Build path
    parser.add_argument(
        "--build_path",
        default=os.environ.get("TDW_BUILD_PATH"),
        help="The path to the build",
    )
    # OpenGL version
    parser.add_argument(
        "--force_glcore42",
        type=bool,
        default=False,
        help="Use OpenGL 4.2 instead of latest system version",
    )
    # Build screen width
    parser.add_argument(
        "--screen_width", default=256, type=int, help="Screen width in pixels"
    )
    # Build screen height
    parser.add_argument(
        "--screen_height", default=256, type=int, help="Screen height in pixels"
    )
    # Render GPUs
    parser.add_argument(
        "--gpus", default="0", type=str, help="GPUs to be used for rendering"
    )
    # Parse the arguments.
    args = parser.parse_args()

    assert args.build_path is not None
    args.gpus = itertools.cycle(args.gpus.split(","))

    return args


if __name__ == "__main__":
    args = _get_binary_manager_args()
    binary_manager = BinaryManager()
    binary_manager.run(args)
