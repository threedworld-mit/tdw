from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian


"""
Different ways to add the same object to a scene.
"""


class AddObjects(Controller):
    def run(self):
        self.start()
        self.communicate(TDWUtils.create_empty_room(20, 20))
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 3, "z": -6},
                                                look_at=TDWUtils.VECTOR3_ZERO))
        model_name = "rh10"

        z = -3

        x = -1.5
        print("With the add_object command (complex syntax but you have maximum control):")
        record = ModelLibrarian().get_record(model_name)
        self.communicate({"$type": "add_object",
                          "name": model_name,
                          "url": record.get_url(),
                          "scale_factor": record.scale_factor,
                          "position": {"x": x, "y": 0, "z": z},
                          "rotation": TDWUtils.VECTOR3_ZERO,
                          "category": record.wcategory,
                          "id": self.get_unique_id()})

        x = 0
        print("With the wrapper function Controller.add_object() "
              "(easy to use, but you can't add additional commands to this frame):")
        self.add_object(model_name=model_name,
                        position={"x": x, "y": 0, "z": z},
                        rotation=TDWUtils.VECTOR3_ZERO, 
                        library="models_core.json")

        x = 1.5
        print("With the wrapper function Controller.get_add_object() "
              "(harder to use, but you can add commands to this frame):")
        self.communicate(self.get_add_object(model_name=model_name,
                                             object_id=self.get_unique_id(),
                                             position={"x": x, "y": 0, "z": 0},
                                             rotation=TDWUtils.VECTOR3_ZERO,
                                             library="models_core.json"))

        print("With the add_object command, minus all optional parameters (the model won't scale properly!):")
        self.communicate({"$type": "add_object",
                          "name": model_name,
                          "url": record.get_url(),
                          "id": self.get_unique_id()})

        print("With the wrapper function Controller.add_object(), minus all optional parameters:")
        self.add_object(model_name)

        print("With the wrapper function Controller.get_add_object(), minus all optional parameters:")
        self.communicate(self.get_add_object(model_name=model_name,
                                             object_id=self.get_unique_id()))


if __name__ == "__main__":
    AddObjects().run()
