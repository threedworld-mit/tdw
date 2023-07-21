import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera


class WindDirection(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.cone_id: int = Controller.get_unique_id()

    def trial(self, scene_name: str) -> None:
        # Add a camera.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 2.27, "y": 2.2, "z": 1.86},
                                   look_at={"x": 0, "y": 0.6, "z": 0})
        self.add_ons.append(camera)
        # Create the scene.
        commands = [Controller.get_add_scene(scene_name=scene_name)]
        # Add a cone. This will indicate wind direction.
        commands.extend(Controller.get_add_physics_object(model_name="cone",
                                                          object_id=self.cone_id,
                                                          library="models_flex.json",
                                                          position={"x": 0, "y": 0.75, "z": -1.288},
                                                          rotation={"x": 90, "y": 0, "z": 0},
                                                          kinematic=True,
                                                          scale_factor={"x": 0.2, "y": 0.3, "z": 0.2}))
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


if __name__ == "__main__":
    c = WindDirection()
    c.trial(scene_name="mm_craftroom_1a")
