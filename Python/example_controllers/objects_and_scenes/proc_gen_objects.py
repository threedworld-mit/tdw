import numpy as np
from tdw.librarian import ModelLibrarian, ModelRecord
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Bounds
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ProcGen(Controller):
    """
    Using procedural generation, add a table to scene and add chairs around the table.
    """

    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    @staticmethod
    def get_longest_extent(record: ModelRecord) -> float:
        left = TDWUtils.vector3_to_array(record.bounds["left"])
        right = TDWUtils.vector3_to_array(record.bounds["right"])
        front = TDWUtils.vector3_to_array(record.bounds["front"])
        back = TDWUtils.vector3_to_array(record.bounds["back"])
        left_right: float = np.linalg.norm(left - right)
        front_back: float = np.linalg.norm(front - back)
        if left_right > front_back:
            return left_right
        else:
            return front_back

    def get_table_placement_coordinate(self, radius: float) -> float:
        q = float(self.rng.uniform(0, 6 - radius))
        if self.rng.random() < 0.5:
            q *= -1
        return q

    def get_chair_position(self, table_center: np.array, table_bound_point: np.array) -> np.array:
        position_to_center = table_bound_point - table_center
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        chair_position = table_bound_point + (position_to_center_normalized * self.rng.uniform(0.5, 0.125))
        chair_position[1] = 0
        return chair_position

    def run(self) -> None:
        librarian = ModelLibrarian()
        tables = librarian.get_all_models_in_wnid("n04379243")
        chairs = librarian.get_all_models_in_wnid("n03001627")
        tables = [record for record in tables if not record.do_not_use]
        chairs = [record for record in chairs if not record.do_not_use]
        table = tables[self.rng.randint(0, len(tables))]
        chair = chairs[self.rng.randint(0, len(chairs))]

        table_extents = ProcGen.get_longest_extent(table)
        chair_extents = ProcGen.get_longest_extent(chair)
        table_placement_radius = table_extents + chair_extents + 1.15
        table_x = self.get_table_placement_coordinate(table_placement_radius)
        table_z = self.get_table_placement_coordinate(table_placement_radius)
        table_id = self.get_unique_id()

        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 self.get_add_object(model_name=table.name,
                                                     position={"x": table_x, "y": 0, "z": table_z},
                                                     rotation={"x": 0, "y": float(self.rng.uniform(-360, 360)), "z": 0},
                                                     object_id=table_id),
                                 {"$type": "send_bounds",
                                  "frequency": "once",
                                  "ids": [table_id]}])
        # We know tha this is the only output data on this frame.
        bounds = Bounds(resp[0])
        # We know that the table is the only object in the output data.
        table_center = np.array(bounds.get_center(0))
        chair_positions = [self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_left(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_right(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_front(0))),
                           self.get_chair_position(table_center=table_center,
                                                   table_bound_point=np.array(bounds.get_back(0)))]
        table_top = bounds.get_top(0)
        camera = ThirdPersonCamera(position={"x": table_top[0] + 1.5, "y": table_top[1] + 0.7, "z": table_top[2] - 2},
                                   look_at=TDWUtils.array_to_vector3(table_top))
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_objects")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=[camera.avatar_id], pass_masks=["_img"], path=path)
        self.add_ons.extend([camera, capture])
        table_bottom = TDWUtils.array_to_vector3(bounds.get_bottom(0))
        commands = []
        for chair_position in chair_positions:
            object_id = self.get_unique_id()
            commands.extend([self.get_add_object(model_name=chair.name,
                                                 position=TDWUtils.array_to_vector3(chair_position),
                                                 object_id=object_id),
                             {"$type": "object_look_at_position",
                              "position": table_bottom,
                              "id": object_id},
                             {"$type": "rotate_object_by",
                              "angle": float(self.rng.uniform(-20, 20)),
                              "id": object_id,
                              "axis": "yaw"}])
        self.communicate(commands)
        self.communicate({"$type": "terminate"})

if __name__ == "__main__":
    c = ProcGen()
    c.run()
