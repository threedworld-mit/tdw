from threading import Thread
import platform
from time import sleep
import zmq
import psutil
import json
import os
from subprocess import Popen
from typing import List, Union, Optional, Tuple, Dict
from tdw.librarian import ModelLibrarian, SceneLibrarian, MaterialLibrarian, HDRISkyboxLibrarian, \
    HumanoidAnimationLibrarian, HumanoidLibrarian, HumanoidAnimationRecord, RobotLibrarian
from tdw.backend.paths import EDITOR_LOG_PATH, PLAYER_LOG_PATH
from tdw.output_data import OutputData, Version, QuitSignal
from tdw.release.build import Build
from tdw.release.pypi import PyPi
from tdw.version import __version__


class Controller(object):
    """
    Base class for all controllers.

    Usage:

    ```python
    from tdw.controller import Controller
    c = Controller()
    c.start()
    ```
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True, check_build_process: bool = False):
        """
        Create the network socket and bind the socket to the port.

        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        :param check_build_process: If True and the build is on the same machine as this controller, continuously check whether the build process is still up.
        """

        # True if a local build process is currently running.
        self._local_build_is_running: bool = False
        # If True, we already quit (suppresses a warning that the build is down).
        self._quit: bool = False

        # Compare the installed version of the tdw Python module to the latest on PyPi.
        # If there is a difference, recommend an upgrade.
        if check_version:
            self._check_pypi_version()

        # Launch the build.
        if launch_build:
            Controller.launch_build(port=port)
        context = zmq.Context()

        self.socket = context.socket(zmq.REP)
        self.socket.bind('tcp://*:' + str(port))

        self.socket.recv()

        # Get the expected name of the process.
        if check_build_process:
            ps = platform.system()
            if ps == "Windows":
                process_name = "TDW.exe"
            elif ps == "Darwin":
                process_name = "TDW.app"
            else:
                process_name = "TDW.x86_64"
            # Get the process ID, if any.
            got_build_process: bool = False
            for q in psutil.process_iter():
                if got_build_process:
                    break
                if q.name() == process_name:
                    # Get the instance of TDW on the correct port.
                    for connection in q.connections():
                        if connection.raddr.port == port:
                            self._local_build_is_running = True
                            build_pid: int = q.pid
                            # Get the ID of the controller process.
                            controller_pid: int = os.getpid()
                            # Start listening for the build process.
                            t = Thread(target=self._build_process_heartbeat, args=([build_pid, controller_pid]))
                            t.daemon = True
                            t.start()
                            got_build_process = True
                            break

        # Set error handling to default values (the build will try to quit on errors and exceptions).
        # Request the version to log it and remember here if the Editor is being used.
        resp = self.communicate([{"$type": "set_error_handling"},
                                 {"$type": "send_version"}])
        self._is_standalone: bool = False
        self._tdw_version: str = ""
        self._unity_version: str = ""
        for r in resp[:-1]:
            if Version.get_data_type_id(r) == "vers":
                v = Version(r)
                self._tdw_version = v.get_tdw_version()
                self._unity_version = v.get_unity_version()
                self._is_standalone = v.get_standalone()
                break
        self.model_librarian: Optional[ModelLibrarian] = None
        self.scene_librarian: Optional[SceneLibrarian] = None
        self.material_librarian: Optional[MaterialLibrarian] = None
        self.hdri_skybox_librarian: Optional[HDRISkyboxLibrarian] = None
        self.humanoid_librarian: Optional[HumanoidLibrarian] = None
        self.humanoid_animation_librarian: Optional[HumanoidAnimationLibrarian] = None
        self.robot_librarian: Optional[RobotLibrarian] = None

        # Compare the version of the tdw module to the build version.
        if check_version and launch_build:
            self._check_build_version()

    def communicate(self, commands: Union[dict, List[dict]]) -> list:
        """
        Send commands and receive output data in response.

        :param commands: A list of JSON commands.

        :return The output data from the build.
        """

        # Don't do anything if the controller already quit.
        if self._quit:
            return []

        if isinstance(commands, list):
            msg = [json.dumps(commands).encode('utf-8')]
        else:
            msg = [json.dumps([commands]).encode('utf-8')]

        # Send the commands.
        self.socket.send_multipart(msg)
        # Receive output data.
        resp = self.socket.recv_multipart()

        # Occasionally, the build's socket will stop receiving messages.
        # If that happens, it will close the socket, create a new socket, and send a dummy output data object.
        # The ID of the dummy object is "ftre" (FailedToReceive).
        # If the controller receives the dummy object, it should re-send its commands.
        # The dummy object is always in an array: [ftre, 0]
        # This way, the controller can easily differentiate it from a response that just has the frame count.
        while len(resp) > 1 and OutputData.get_data_type_id(resp[0]) == "ftre":
            self.socket.send_multipart(msg)
            resp = self.socket.recv_multipart()

        # Check if we've received a quit signal. If we have, check if there was an error.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "quit":
                if not QuitSignal(resp[i]).get_ok():
                    print("The build quit due to an error. Check the build log for more info.")
                    self._print_build_log()
                self._local_build_is_running = False
                self._quit = True
                break

        # Return the output data from the build.
        return resp

    def start(self, scene="ProcGenScene") -> None:
        """
        Init TDW.

        :param scene: The scene to load.
        """

        self.communicate([{"$type": "load_scene", "scene_name": scene}])

    def get_add_object(self, model_name: str, object_id: int, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str = "") -> dict:
        """
        Returns a valid add_object command.

        :param model_name: The name of the model.
        :param position: The position of the model.
        :param rotation: The starting rotation of the model, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.

        :return An add_object command that the controller can then send.
        """

        if self.model_librarian is None or (library != "" and self.model_librarian.library != library):
            self.model_librarian = ModelLibrarian(library=library)

        record = self.model_librarian.get_record(model_name)

        return {"$type": "add_object",
                "name": model_name,
                "url": record.get_url(),
                "scale_factor": record.scale_factor,
                "position": position,
                "rotation": rotation,
                "category": record.wcategory,
                "id": object_id}

    def get_add_material(self, material_name: str, library: str = "") -> dict:
        """
        Returns a valid add_material command.

        :param material_name: The name of the material.
        :param library: The path to the records file. If left empty, the default library will be selected. See `MaterialLibrarian.get_library_filenames()` and `MaterialLibrarian.get_default_library()`.

        :return An add_material command that the controller can then send.
        """

        if self.material_librarian is None:
            self.material_librarian = MaterialLibrarian(library=library)

        record = self.material_librarian.get_record(material_name)
        return {"$type": "add_material",
                "name": material_name,
                "url": record.get_url()}

    def get_add_scene(self, scene_name: str, library: str = "") -> dict:
        """
        Returns a valid add_scene command.

        :param scene_name: The name of the scene.
        :param library: The path to the records file. If left empty, the default library will be selected. See `SceneLibrarian.get_library_filenames()` and `SceneLibrarian.get_default_library()`.

        :return An add_scene command that the controller can then send.
        """

        if self.scene_librarian is None:
            self.scene_librarian = SceneLibrarian(library=library)

        record = self.scene_librarian.get_record(scene_name)
        return {"$type": "add_scene",
                "name": scene_name,
                "url": record.get_url()}

    def get_add_hdri_skybox(self, skybox_name: str, library: str = "") -> dict:
        """
        Returns a valid add_hdri_skybox command.

        :param skybox_name: The name of the skybox.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HDRISkyboxLibrarian.get_library_filenames()` and `HDRISkyboxLibrarian.get_default_library()`.

        :return An add_hdri_skybox command that the controller can then send.
        """

        if self.hdri_skybox_librarian is None:
            self.hdri_skybox_librarian = HDRISkyboxLibrarian(library=library)

        record = self.hdri_skybox_librarian.get_record(skybox_name)
        return {"$type": "add_hdri_skybox",
                "name": skybox_name,
                "url": record.get_url(),
                "exposure": record.exposure,
                "initial_skybox_rotation": record.initial_skybox_rotation,
                "sun_elevation": record.sun_elevation,
                "sun_initial_angle": record.sun_initial_angle,
                "sun_intensity": record.sun_intensity}

    def get_add_humanoid(self, humanoid_name: str, object_id: int, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str ="") -> dict:
        """
        Returns a valid add_humanoid command.

        :param humanoid_name: The name of the humanoid.
        :param position: The position of the humanoid.
        :param rotation: The starting rotation of the humanoid, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HumanoidLibrarian.get_library_filenames()` and `HumanoidLibrarian.get_default_library()`.
        :param object_id: The ID of the new object.

        :return An add_humanoid command that the controller can then send.
        """

        if self.humanoid_librarian is None or (library != "" and self.humanoid_librarian.library != library):
            self.humanoid_librarian = HumanoidLibrarian(library=library)

        record = self.humanoid_librarian.get_record(humanoid_name)

        return {"$type": "add_humanoid",
                "name": humanoid_name,
                "url": record.get_url(),
                "position": position,
                "rotation": rotation,
                "id": object_id}

    def get_add_humanoid_animation(self, humanoid_animation_name: str, library="") -> (dict, HumanoidAnimationRecord):
        """
        Returns a valid add_humanoid_animation command and the record (which you will need to play an animation).

        :param humanoid_animation_name: The name of the animation.
        :param library: The path to the records file. If left empty, the default library will be selected. See `HumanoidAnimationLibrarian.get_library_filenames()` and `HumanoidAnimationLibrarian.get_default_library()`.

        :return An add_humanoid_animation command that the controller can then send.
        """

        if self.humanoid_animation_librarian is None:
            self.humanoid_animation_librarian = HumanoidAnimationLibrarian(library=library)

        record = self.humanoid_animation_librarian.get_record(humanoid_animation_name)
        return {"$type": "add_humanoid_animation",
                "name": humanoid_animation_name,
                "url": record.get_url()}, record

    def get_add_robot(self, name: str, robot_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict:
        """
        Returns a valid add_robot command.

        :param name: The name of the robot.
        :param robot_id: A unique ID for the robot.
        :param position: The initial position of the robot. If None, the position will be (0, 0, 0).
        :param rotation: The initial rotation of the robot in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `RobotLibrarian.get_library_filenames()` and `RobotLibrarian.get_default_library()`.

        :return An `add_robot` command that the controller can then send.
        """

        if self.robot_librarian is None:
            self.robot_librarian = RobotLibrarian(library=library)

        record = self.robot_librarian.get_record(name)

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}

        assert record is not None, f"Robot metadata record not found: {name}"
        return {"$type": "add_robot",
                "id": robot_id,
                "position": position,
                "rotation": rotation,
                "name": name,
                "url": record.get_url()}

    def load_streamed_scene(self, scene="tdw_room") -> None:
        """
        Load a streamed scene. This is equivalent to: `c.communicate(c.get_add_scene(scene))`

        :param scene: The name of the streamed scene.
        """

        self.communicate(self.get_add_scene(scene))

    def add_object(self, model_name: str, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str= "") -> int:
        """
        Add a model to the scene. This is equivalent to: `c.communicate(c.get_add_object())`

        :param model_name: The name of the model.
        :param position: The position of the model.
        :param rotation: The starting rotation of the model, in Euler angles.
        :param library: The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`.

        :return The ID of the new object.
        """

        object_id = Controller.get_unique_id()
        self.communicate(self.get_add_object(model_name, object_id, position, rotation, library))

        return object_id

    def get_version(self) -> Tuple[str, str]:
        """
        Send a send_version command to the build.

        :return The TDW version and the Unity Engine version.
        """

        resp = self.communicate({"$type": "send_version"})
        for r in resp[:-1]:
            if Version.get_data_type_id(r) == "vers":
                v = Version(r)
                return v.get_tdw_version(), v.get_unity_version()
        if len(resp) == 1:
            raise Exception("Tried receiving version output data but didn't receive anything!")
        raise Exception(f"Expected output data with ID version but got: " + Version.get_data_type_id(resp[0]))

    @staticmethod
    def get_unique_id() -> int:
        """
        Generate a unique integer. Useful when creating objects.

        :return The new unique ID.
        """

        return int.from_bytes(os.urandom(3), byteorder='big')

    @staticmethod
    def get_frame(frame: bytes) -> int:
        """
        Converts the frame byte array to an integer.

        :param frame: The frame as bytes.

        :return The frame as an integer.
        """

        return int.from_bytes(frame, byteorder='big')

    @staticmethod
    def launch_build(port: int = 1071) -> None:
        """
        Launch the build. If a build doesn't exist at the expected location, download one to that location.

        :param port: The socket port.
        """

        # Download the build.
        need_to_download = False
        if not Build.BUILD_PATH.exists():
            print(f"Couldn't find build at {Build.BUILD_PATH}\nDownloading now...")
            need_to_download = True
        else:
            # Check versions.
            build_version_path = Build.BUILD_ROOT_DIR.joinpath("TDW/version.txt")
            if build_version_path.exists():
                build_version = build_version_path.read_text().strip()
            else:
                build_version = "(unknown!)"
            if build_version != __version__:
                print(f"Python version is {__version__} but the build version is {build_version}.\n"
                      f"Downloading version {__version__} of the build now...")
                need_to_download = True

        # Download a new version of the build.
        if need_to_download:
            success = Build.download()
            if not success:
                print("You need to launch your own build.")
        else:
            success = True
        # Launch the build.
        if success:
            Popen([str(Build.BUILD_PATH.resolve()), "-port "+str(port)])

    def _check_build_version(self, version: str = __version__, build_version: str = None) -> None:
        """
        Check the version of the build. If there is no build, download it.
        If the build is of the wrong version, recommend an upgrade.

        :param version: The version of TDW. You can set this to an arbitrary version for testing purposes.
        :param build_version: If not None, this overrides the expected build version. Only override for debugging.
        """

        # Override the build version for testing.
        if build_version is not None:
            self._tdw_version = build_version
        print(f"Build version {self._tdw_version}\nUnity Engine {self._unity_version}\n"
              f"Python tdw module version {version}")

    def _build_process_heartbeat(self, build_pid: int, controller_pid: int) -> None:
        """
        Check whether the build and the main controller processes are still up.
        Run this in a thread, and only when the build is running local.

        :param build_pid: The build process ID.
        :param controller_pid: The controller process ID.
        """

        try:
            while self._local_build_is_running:
                # If the main thread is down or the build is down, stop.
                if not psutil.pid_exists(build_pid) or not psutil.pid_exists(controller_pid):
                    self._local_build_is_running = False
                    sleep(1)
            if not self._quit:
                self._quit = True
                print("The build is probably down due to an unhandled exception."
                      " Check the build log for more info.")
                self._print_build_log()
            self._local_build_is_running = False
        finally:
            # Kill the remaining processes.
            for pid in [build_pid, controller_pid]:
                if psutil.pid_exists(pid):
                    os.kill(pid, 9)

    def _print_build_log(self) -> None:
        """
        Print a message indicating where the build log is located.
        """

        if self._is_standalone:
            log_path = PLAYER_LOG_PATH
        else:
            log_path = EDITOR_LOG_PATH
        print(f"If the build is on the same machine as this controller, the log path is probably "
              f"{str(log_path.resolve())}")
        print(f"If the build is on a remote Linux server, the log path is probably"
              f" ~/.config/unity3d/MIT/TDW/Player.log (where ~ is your home directory)")

    @staticmethod
    def _check_pypi_version(v_installed_override: str = None, v_pypi_override: str = None) -> None:
        """
        Compare the version of the tdw Python module to the latest on PyPi.
        If there is a mismatch, offer an upgrade recommendation.

        :param v_installed_override: Override for the installed version. Change this to debug.
        :param v_pypi_override: Override for the PyPi version. Change this to debug.
        """

        # Get the version of the installed tdw module.
        installed_tdw_version = PyPi.get_installed_tdw_version()
        # Get the latest version of the tdw module on PyPi.
        pypi_version = PyPi.get_pypi_version()

        # Apply overrides
        if v_installed_override is not None:
            installed_tdw_version = v_installed_override
        if v_pypi_override is not None:
            pypi_version = v_pypi_override

        # If there is a mismatch, recommend an upgrade.
        if installed_tdw_version != pypi_version:
            # Strip the installed version of the post-release suffix (e.g. 1.6.3.4 to 1.6.3).
            stripped_installed_version = PyPi.strip_post_release(installed_tdw_version)
            # This message is here only for debugging.
            if stripped_installed_version != __version__:
                print(f"Your installed version: {stripped_installed_version} "
                      f"doesn't match tdw.version.__version__: {__version__} "
                      f"(this may be because you're using code from the tdw repo that is ahead of PyPi).")
            # Strip the latest PyPi version of the post-release suffix.
            stripped_pypi_version = PyPi.strip_post_release(pypi_version)
            print(f"You are using TDW {installed_tdw_version} but version {pypi_version} is available.")

            # If user is behind by a post release, recommend an upgrade to the latest.
            # (Example: installed version is 1.6.3.4 and PyPi version is 1.6.3.5)
            if stripped_installed_version == stripped_pypi_version:
                print(f"Upgrade to the latest version of TDW:\npip3 install tdw -U")

            # Using a version behind the latest (e.g. latest is 1.6.3 and installed is 1.6.2)
            # If the user is behind by a major or minor release, recommend either upgrading to a minor release
            # or to a major release.
            # (Example: installed version is 1.6.3.4 and PyPi version is 1.7.0.0)
            else:
                installed_major = PyPi.get_major_release(stripped_installed_version)
                pypi_minor = PyPi.get_latest_minor_release(stripped_installed_version)
                # Minor release mis-match.
                if PyPi.strip_post_release(pypi_minor) != stripped_installed_version:
                    print(f"To upgrade to the last version of 1.{installed_major}:\n"
                          f"pip3 install tdw=={pypi_minor}")
                pypi_major = PyPi.get_major_release(stripped_pypi_version)
                # Major release mis-match.
                if installed_major != pypi_major:
                    # Offer to upgrade to a major release.
                    print(f"Consider upgrading to the latest version of TDW ({stripped_pypi_version}):"
                          f"\npip3 install tdw -U")
        else:
            print("Your installed tdw Python module is up to date with PyPi.")
