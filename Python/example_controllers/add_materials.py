from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import MaterialLibrarian
from time import sleep


"""
Different ways to add the same material to a scene_data.
"""


class AddMaterials(Controller):
    def create_scene(self):
        """
        Initialize a blank room.
        """

        self.start()
        commands = [TDWUtils.create_empty_room(12, 12)]
        commands.extend(TDWUtils.create_avatar(position={"x": 5, "y": 10, "z": 5}, look_at=TDWUtils.VECTOR3_ZERO))
        self.communicate(commands)

    def run(self):
        self.create_scene()

        print("Using Controller.get_add_material wrapper function:")

        self.communicate([self.get_add_material("parquet_long_horizontal_clean"),
                          {"$type": "set_proc_gen_floor_material",
                           "name": "parquet_long_horizontal_clean"}])

        sleep(5)

        self.create_scene()

        print("Using the add_material command without any wrappers:")
        lib = MaterialLibrarian()
        record = lib.get_record("parquet_long_horizontal_clean")
        self.communicate([{"$type": "add_material",
                           "name": record.name,
                           "url": record.get_url()},
                          {"$type": "set_proc_gen_floor_material",
                           "name": "parquet_long_horizontal_clean"}])


if __name__ == "__main__":
    AddMaterials().run()
