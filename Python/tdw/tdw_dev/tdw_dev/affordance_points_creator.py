from math import radians, sin, cos
from typing import List, Dict
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.mouse import Mouse
from tdw.add_ons.keyboard import Keyboard
from tdw.add_ons.ui import UI
from tdw.output_data import OutputData, Raycast, ImageSensors


class _Camera(ThirdPersonCamera):
    """
    A third-person camera that tracks the forward directional vector.
    """

    def __init__(self, avatar_id: str = None):
        super().__init__(avatar_id=avatar_id)
        self.forward: Dict[str, float] = TDWUtils.VECTOR3_ZERO

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.append({"$type": "send_image_sensors",
                         "frequency": "always"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        super().on_send(resp=resp)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imse":
                images_sensors = ImageSensors(resp[i])
                self.forward = TDWUtils.array_to_vector3(np.array(images_sensors.get_sensor_forward(0)))
                break


class AffordancePointsCreator(Controller):
    """
    Draw affordance points on an object.

    Controls:

    - WASD: Rotate camera.
    - Scroll wheel: Zoom.
    - Left click: Add affordance points.
    - Right click: Remove affordance points.
    - Spacebar: Save and quit (the metadata record will be updated).
    - Escape: Quit.
    """

    def __init__(self, screen_width: int = 1024, screen_height: int = 1024,
                 rotate_speed: float = 3, move_speed: float = 0.1,
                 min_point_distance: float = 0.025, eraser_radius: float = 0.025,
                 port: int = 1071, check_version: bool = True, launch_build: bool = True):
        """
        :param screen_width: The screen width in pixels.
        :param screen_height: The screen height in pixels.
        :param rotate_speed: The speed of the camera rotation in degrees per `communicate()` call.
        :param move_speed: The camera movement (zoom) speed in meters per `communicate()` call.
        :param min_point_distance: The minimum distance between affordance points. This prevents densely-packed affordance points that are at nearly the same position.
        :param eraser_radius: The radius of the eraser when right-clicking to remove affordance points.
        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor.
        """

        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self._done: bool = False
        self._save: bool = False
        # Add UI for controls.
        ui = UI()
        # Create the camera.
        self._camera: _Camera = _Camera(avatar_id="a")
        self._rotate_speed: float = rotate_speed
        self._move_speed: float = move_speed
        self._min_point_distance: float = min_point_distance
        self._eraser_radius: float = eraser_radius
        # Add a keyboard listener.
        keyboard = Keyboard()
        # Quit when the escape key is pressed.
        keyboard.listen(key="Escape", function=self._quit)
        camera_events = ["press", "hold"]
        # Rotate when WASD keys are pressed.
        keyboard.listen(key="A",
                        function=self._rotate_camera_counterclockwise,
                        events=camera_events)
        keyboard.listen(key="D",
                        function=self._rotate_camera_clockwise,
                        events=camera_events)
        keyboard.listen(key="W",
                        function=self._rotate_camera_up,
                        events=camera_events)
        keyboard.listen(key="S",
                        function=self._rotate_camera_down,
                        events=camera_events)
        # Save the affordance points when the spacebar is pressed.
        keyboard.listen(key="Space",
                        function=self._save_affordance_points)
        # Add a mouse listener.
        self._mouse: Mouse = Mouse()
        # Add the add-ons.
        self.add_ons.extend([ui, keyboard, self._mouse, self._camera])
        # Initialize the scene.
        self.communicate([{"$type": "set_screen_size",
                           "width": screen_width,
                           "height": screen_height},
                          {"$type": "set_target_framerate",
                           "framerate": 60},
                          {"$type": "create_empty_environment"},
                          {"$type": "set_post_process",
                           "value": False}])
        ui.add_text(text="WASD: Rotate\nScroll wheel: Zoom\nSpacebar: Save and quit\nEscape: Quit",
                    font_size=18,
                    color={"r": 0, "g": 0, "b": 0, "a": 1},
                    anchor={"x": 0, "y": 1},
                    pivot={"x": 0, "y": 1},
                    position={"x": 6, "y": -6},
                    raycast_target=False)
        ui.add_text(text="Left click: Add\nRight click: Remove",
                    font_size=18,
                    color={"r": 0, "g": 0, "b": 0, "a": 1},
                    anchor={"x": 1, "y": 1},
                    pivot={"x": 1, "y": 1},
                    position={"x": -6, "y": -6},
                    raycast_target=False)
        self.communicate([])

    def run(self, model_name: str, library_name: str) -> None:
        """
        Add an object to the scene and draw affordance points.

        :param model_name: The name of the model.
        :param library_name: The name of the model's library.
        """

        # Cache the model library.
        if library_name not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS[library_name] = ModelLibrarian(library_name)
        is_core = library_name == "models_core.json"
        # Cache the full model library.
        if is_core and "models_full.json" not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS["models_full.json"] = ModelLibrarian("models_full.json")
        # Fetch the model record.
        record: ModelRecord = Controller.MODEL_LIBRARIANS[library_name].get_record(model_name)
        # Try to find a z position that will fit the object in the viewport.
        front_z = record.bounds["front"]["z"]
        width = float(np.linalg.norm(record.bounds["left"]["x"] - record.bounds["right"]["x"]))
        position_marker_size = width * 0.1
        camera_z = (width / 2) * np.tan(np.deg2rad(60)) + front_z * 2
        camera_y = record.bounds["center"]["y"]
        # Teleport to an initial position.
        self._camera.teleport(position={"x": 0, "y": camera_y, "z": camera_z})
        # Look at the object.
        self._camera.look_at(target={"x": 0, "y": camera_y, "z": 0})
        object_id = Controller.get_unique_id()
        # Create an empty environment and an object.
        # The object won't respond to gravity, but will also be non-kinematic so it can respond to raycasts.
        # Disable post-processing.
        initialization_commands: List[dict] = [Controller.get_add_object(model_name=model_name,
                                                                         object_id=object_id,
                                                                         library=library_name),
                                               {"$type": "set_kinematic_state",
                                                "id": object_id,
                                                "is_kinematic": False,
                                                "use_gravity": False}]
        # Draw existing affordance points.
        for existing_affordance_point in record.affordance_points:
            initialization_commands.append({"$type": "add_position_marker",
                                            "scale": position_marker_size,
                                            "position": existing_affordance_point})
        # Send the initialization commands.
        resp = self.communicate(initialization_commands)
        affordance_points: List[np.ndarray] = list()
        # Run until we're done.
        self._done = False
        self._save = False
        raycast_id = Controller.get_unique_id()
        while not self._done:
            commands: List[dict] = []
            # Check if we're drawing over anything.
            if (self._mouse.left_button_pressed or self._mouse.left_button_held) and self._mouse.mouse_is_over_object:
                # Get the mouse raycast.
                mouse_raycast_normal = np.array([0, 0, 0])
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "rayc":
                        raycast = Raycast(resp[i])
                        if raycast.get_raycast_id() == self._mouse.raycast_id:
                            mouse_raycast_normal = np.array(raycast.get_normal())
                            break
                # Sphercast along the mouse raycast's normal vector.
                resp = self.communicate({"$type": "send_raycast",
                                         "origin": TDWUtils.array_to_vector3(self._mouse.world_position + mouse_raycast_normal * 1.1),
                                         "destination": TDWUtils.array_to_vector3(self._mouse.world_position),
                                         "id": raycast_id})
                # Get the raycast.
                for i in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[i])
                    if r_id == "rayc":
                        raycast = Raycast(resp[i])
                        if raycast.get_raycast_id() == raycast_id and raycast.get_hit() and raycast.get_hit_object():
                            raycast_position = np.array(raycast.get_point())
                            # Check for clustering.
                            too_close = False
                            for point in affordance_points:
                                if np.linalg.norm(point - raycast_position) < self._min_point_distance:
                                    too_close = True
                                    break
                            # Add an affordance point.
                            if not too_close:
                                affordance_points.append(raycast_position)
                                # Add a position marker.
                                commands.append({"$type": "add_position_marker",
                                                 "scale": position_marker_size,
                                                 "position": TDWUtils.array_to_vector3(raycast_position)})
            # Erase affordance points.
            elif (self._mouse.right_button_pressed or self._mouse.right_button_held) and self._mouse.mouse_is_over_object:
                # Only add affordance points outside of the sphere.
                affordance_points = [a for a in affordance_points if np.linalg.norm(a - self._mouse.world_position) >= self._eraser_radius]
                commands.append({"$type": "remove_position_markers"})
                commands.extend([{"$type": "add_position_marker",
                                  "position": TDWUtils.array_to_vector3(a),
                                  "scale": position_marker_size} for a in affordance_points])
            # Move the camera forward or backward.
            scroll_wheel_delta = self._mouse.scroll_wheel_delta[1]
            if scroll_wheel_delta != 0:
                camera_distance = np.linalg.norm(TDWUtils.vector3_to_array(self._camera.position) - np.array([0, 0, 0]))
                ms = self._move_speed if scroll_wheel_delta > 0 else -self._move_speed
                # Clamp the camera distance so that the look at rotation doesn't flip.
                if (ms > 0 and camera_distance > width) or (ms < 0 and camera_distance < 100):
                    # Teleport the camera by the move speed along the forward vector.
                    self._camera.teleport(position={"x": self._camera.position["x"] + self._camera.forward["x"] * ms,
                                                    "y": self._camera.position["y"] + self._camera.forward["y"] * ms,
                                                    "z": self._camera.position["z"] + self._camera.forward["z"] * ms})
            # Send the commands.
            resp = self.communicate(commands)
        # Save the affordance points data.
        if self._save:
            record.affordance_points = [TDWUtils.array_to_vector3(a) for a in affordance_points]
            Controller.MODEL_LIBRARIANS[library_name].add_or_update_record(record=record, overwrite=True, write=True)
            # Update models_full.json
            if library_name == "models_core.json":
                Controller.MODEL_LIBRARIANS["models_full.json"].add_or_update_record(record=record, overwrite=True, write=True)
        # Destroy the object and the position markers.
        self.communicate([{"$type": "destroy_object",
                           "id": object_id},
                          {"$type": "remove_position_markers"}])

    def _quit(self) -> None:
        """
        Quit the simulation.
        """

        self._done = True
        self._save = False

    def _save_affordance_points(self) -> None:
        """
        Quit the simulation and save the affordance points.
        """

        self._done = True
        self._save = True

    def _rotate_camera_clockwise(self) -> None:
        """
        Rotate the camera clockwise.
        """

        self._rotate_camera_yaw(direction=1)

    def _rotate_camera_counterclockwise(self) -> None:
        """
        Rotate the camera counterclockwise.
        """

        self._rotate_camera_yaw(direction=-1)

    def _rotate_camera_up(self) -> None:
        """
        Rotate the camera up.
        """

        self._rotate_camera_pitch(direction=1)

    def _rotate_camera_down(self) -> None:
        """
        Rotate the camera down.
        """

        self._rotate_camera_pitch(direction=-1)

    def _rotate_camera_yaw(self, direction: int) -> None:
        """
        Rotate the camera around the yaw axis.

        :param direction: The direction of the rotation.
        """

        rad = radians(self._rotate_speed * direction)
        x_rot = cos(rad) * self._camera.position["x"] - sin(rad) * self._camera.position["z"]
        z_rot = sin(rad) * self._camera.position["x"] + cos(rad) * self._camera.position["z"]
        self._camera.teleport(position={"x": x_rot, "y": self._camera.position["y"], "z": z_rot})

    def _rotate_camera_pitch(self, direction: int) -> None:
        """
        Rotate the camera around the pitch axis.

        :param direction: The direction of the rotation.
        """

        rad = radians(self._rotate_speed * direction)
        z_rot = cos(rad) * self._camera.position["z"] - sin(rad) * self._camera.position["y"]
        y_rot = sin(rad) * self._camera.position["z"] + cos(rad) * self._camera.position["y"]
        self._camera.teleport(position={"x": self._camera.position["x"],
                                        "y": y_rot,
                                        "z": z_rot})
