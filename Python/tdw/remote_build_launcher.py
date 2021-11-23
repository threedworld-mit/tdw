from typing import List
import time
from threading import Thread
import socket as sock
from contextlib import closing
import zmq


class RemoteBuildLauncher:
    """
    Connect to a remote binary_manager daemon and launch an instance of a TDW build.
    """

    @staticmethod
    def launch_build(listener_port: int, build_address: str, controller_address: str) -> dict:
        """
        Connect to a remote binary_manager daemon and launch an instance of a TDW build.

        Returns the necessary information for a local controller to connect.
        Use this function to automatically launching binaries on remote (or local) nodes, and to
        automatically shut down the build after controller is finished. Call in the constructor
        of a controller and pass the build_port returned in build_info to the parent Controller class.

        :param listener_port: The port launch_binaries is listening on.
        :param build_address: Remote IP or hostname of node running launch_binaries.
        :param controller_address: IP or hostname of node running controller.

        :return The build_info dictionary containing build_port.
        """

        context = zmq.Context()
        # noinspection PyUnresolvedReferences
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://" + build_address + ":%s" % listener_port)
        build_info = RemoteBuildLauncher._send_start_build(socket, controller_address)
        thread = Thread(target=RemoteBuildLauncher._keep_alive_thread,
                        args=(socket, build_info))
        thread.setDaemon(True)
        thread.start()
        return build_info

    @staticmethod
    def get_unity_args(arg_dict: dict) -> List[str]:
        """
        :param arg_dict: A dictionary of arguments. Key=The argument prefix (e.g. port) Value=Argument value.

        :return The formatted command line string that is accepted by unity arg parser.
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
    def find_free_port() -> int:
        """
        :return A free socket port.
        """

        with closing(sock.socket(sock.AF_INET, sock.SOCK_STREAM)) as s:
            s.bind(("", 0))
            return int(s.getsockname()[1])

    @staticmethod
    def _send_start_build(socket, controller_address: str) -> dict:
        """
        This sends a command to the launch_binaries daemon running on a remote node
        to start a binary connected to the given controller address.

        :param socket: The zmq socket.
        :param controller_address: The host name or ip address of node running the controller.

        :return Build info dictionary containing build port.
        """
        request = {"type": "start_build",
                   "controller_address": controller_address}
        socket.send_json(request)
        build_info = socket.recv_json()
        return build_info

    @staticmethod
    def _send_keep_alive(socket, build_info: dict) -> dict:
        """
        This sends a command to the launch_binaries daemon running on a remote node
        to mark a given binary as still alive, preventing garbage collection.

        :param socket: The zmq socket.
        :param build_info: A diciontary containing the build_port.

        :return a heartbeat indicating build is still alive.
        """

        build_port = build_info["build_port"]
        request = {"type": "keep_alive", "build_port": build_port}
        socket.send_json(request)
        heartbeat = socket.recv_json()
        return heartbeat

    @staticmethod
    def _send_kill_build(socket, build_info: dict) -> dict:
        """
        This sends a command to the launch_binaries daemon running on a remote node to terminate a given binary.

        :param socket: The zmq socket.
        :param build_info: A diciontary containing the build_port.

        :return A kill_status indicating build has been succesfully terminated.
        """

        build_port = build_info["build_port"]
        request = {"type": "kill_build", "build_port": build_port}
        socket.send_json(request)
        kill_status = socket.recv_json()
        return kill_status

    @staticmethod
    def _keep_alive_thread(socket, build_info: dict) -> None:
        """
        This is a wrapper around the keep alive command to be executed in a separate thread.

        :param socket: The zmq socket.
        :param build_info: A diciontary containing the build_port.
        """
        while True:
            RemoteBuildLauncher._send_keep_alive(socket, build_info)
            time.sleep(60)
