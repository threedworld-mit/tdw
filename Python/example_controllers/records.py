from random import choice
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import MaterialLibrarian, ModelLibrarian, MaterialRecord, ModelRecord


"""
- Use Librarian objects to search for model and material records.
- Set the visual material(s) of an object.
For documentation, see `Documentation/python/librarian.md`.
"""


class Records(Controller):
    def run(self):
        self.start()

        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))

        material_librarian = MaterialLibrarian()

        # Fetch a random wood material record.
        wood_records = material_librarian.get_all_materials_of_type("Wood")
        wood_record: MaterialRecord = choice(wood_records)
        # Fetch a random concrete record material.
        concrete_records = material_librarian.get_all_materials_of_type("Concrete")
        concrete_record: MaterialRecord = choice(concrete_records)

        # Set the floor material.
        # Set the floor material texture scale.
        # Set the walls material.
        # Set the wall material texture scale.
        self.communicate([self.get_add_material(wood_record.name),
                          self.get_add_material(concrete_record.name),
                          {"$type": "set_proc_gen_floor_material",
                           "name": wood_record.name},
                          {"$type": "set_proc_gen_floor_texture_scale",
                           "scale": {"x": 8, "y": 8}},
                          {"$type": "set_proc_gen_walls_material",
                           "name": concrete_record.name},
                          {"$type": "set_proc_gen_walls_texture_scale",
                           "scale": {"x": 2, "y": 8}}
                          ])

        # Create a random table.
        model_librarian = ModelLibrarian()
        wnids = model_librarian.get_model_wnids_and_wcategories()
        table_wnid = [wnid for wnid in wnids if wnids[wnid] == "table"][0]
        table_records = model_librarian.get_all_models_in_wnid(table_wnid)
        # Filter out unusable tables.
        table_records = [t for t in table_records if not t.do_not_use]
        table_record: ModelRecord = choice(table_records)
        # Add the table.
        table_id = self.add_object(table_record.name)

        # Set a random visual material for each sub-object in the model.
        commands = list()
        for sub_object in table_record.substructure:
            for i in range(len(sub_object["materials"])):
                material_record: MaterialRecord = choice(material_librarian.records)
                commands.extend([self.get_add_material(material_record.name),
                                 {"$type": "set_visual_material",
                                  "id": table_id,
                                  "material_name": material_record.name,
                                  "object_name": sub_object["name"],
                                  "material_index": i}])
        self.communicate(commands)

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 4, "y": 3, "z": 2},
                                                look_at=TDWUtils.VECTOR3_ZERO))


if __name__ == "__main__":
    Records().run()
