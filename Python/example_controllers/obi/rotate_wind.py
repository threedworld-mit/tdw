import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.obi import Obi
from tdw.add_ons.image_capture import ImageCapture
from tdw.obi_data.wind_source import WindSource
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class RotateWind(Controller):
    """
    Line up a row of small objects on a table.

    Add a wind source. Rotate the wind source per communicate() call to knock over the objects.

    Add a cone to point in the direction of the wind.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.cone_id: int = Controller.get_unique_id()
        self.wind_id: int = Controller.get_unique_id()
        self.obi = Obi()

    def trial(self, scene_name: str) -> None:
        # Add a camera and image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 2.27, "y": 2.2, "z": 1.86},
                                   look_at={"x": 0, "y": 0.6, "z": 0})
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("rotate_wind")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"],
                               path=path)
        # Add Obi. Don't add colliders to the cone.
        self.obi = Obi(exclude=[self.cone_id])
        self.add_ons.extend([camera, capture, self.obi])
        # Add a wind source.
        wind_x = 0
        wind_y = 0.75
        wind_z = -1.1
        wind_rotation = -60
        wind_source = WindSource(wind_id=self.wind_id,
                                 position={"x": wind_x, "y": wind_y, "z": wind_z},
                                 rotation={"x": 0, "y": wind_rotation, "z": 0},
                                 emitter_radius=0.2,
                                 capacity=2000,
                                 lifespan=0.5,
                                 smoothing=1,
                                 speed=14)
        self.obi.wind_sources[self.wind_id] = wind_source
        # Create the scene.
        commands = [Controller.get_add_scene(scene_name=scene_name)]
        # Add a cone. This will indicate wind direction.
        cone_euler_angles = {"x": 90, "y": wind_rotation, "z": 0}
        commands.extend(Controller.get_add_physics_object(model_name="cone",
                                                          object_id=self.cone_id,
                                                          library="models_flex.json",
                                                          position={"x": wind_x, "y": wind_y, "z": wind_z - 0.3},
                                                          rotation=cone_euler_angles,
                                                          kinematic=True,
                                                          scale_factor={"x": 0.2, "y": 0.3, "z": 0.2}))
        commands.append({"$type": "set_color",
                         "id": self.cone_id,
                         "color": {"r": 1, "g": 0, "b": 0, "a": 1}})
        # Add two tables.
        table_model_name = "live_edge_coffee_table"
        table_x0 = -1.231
        z = 0.645
        commands.extend(Controller.get_add_physics_object(model_name=table_model_name,
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": table_x0, "y": 0, "z": z},
                                                          library="models_core.json",
                                                          kinematic=True))
        # Get the dimensions of the tables.
        table_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(table_model_name)
        table_extents = TDWUtils.get_bounds_extents(table_record.bounds)
        h = float(table_extents[1])
        w = float(table_extents[0])
        # Use the width to position the second table.
        table_x1 = table_x0 + w / 2
        commands.extend(Controller.get_add_physics_object(model_name=table_model_name,
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": table_x1, "y": 0, "z": z},
                                                          library="models_core.json",
                                                          kinematic=True))
        # Get the vase record.
        vase_model_name = "vase_02"
        vase_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(vase_model_name)
        vase_extents = TDWUtils.get_bounds_extents(vase_record.bounds)
        vase_w = float(vase_extents[0])
        # Get x coordinates for the vases.
        vase_xs = np.arange(table_x0 - w / 2 + vase_w / 2, table_x1 + w / 2 - vase_w / 2, step=vase_w * 1.1)
        # Add the vases.
        for vase_x in vase_xs:
            commands.extend(Controller.get_add_physics_object(model_name=vase_model_name,
                                                              object_id=Controller.get_unique_id(),
                                                              position={"x": float(vase_x), "y": h, "z": z},
                                                              library="models_core.json"))
        self.communicate(commands)
        # Rotate the wind.
        for angle in [90, -10]:
            self.rotate_wind_by(angle=angle, initial_angle=wind_rotation)

    def rotate_wind_by(self, angle: float, initial_angle: float) -> None:
        wind: WindSource = self.obi.wind_sources[self.wind_id]
        # Start rotating by the angle.
        wind.rotate_by(angle=angle, da=0.2, axis="yaw")
        self.communicate([])
        while wind.is_rotating():
            # Rotate the cone to match the rotation of the wind. Continue until the wind emitter is done rotating.
            wind_angle, axis = wind.get_rotation()
            self.communicate([{"$type": "rotate_object_to_euler_angles",
                               "id": self.cone_id,
                               "euler_angles": {"x": 90, "y": wind_angle + initial_angle, "z": 0}}])


if __name__ == "__main__":
    c = RotateWind()
    c.trial(scene_name="box_room_2018")
    c.communicate({"$type": "terminate"})
