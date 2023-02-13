import json
from pathlib import Path
from typing import List
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ObjectDataWriter(ObjectManager):
    """
    A custom sub-class of ObjectManager that writes the position and rotation of each object per frame.
    """

    def __init__(self, output_directory: Path, transforms: bool = True, rigidbodies: bool = False, bounds: bool = False):
        self.output_directory: Path = output_directory
        if not output_directory.exists():
            output_directory.mkdir(parents=True)
        self.frame: int = 0
        super().__init__(transforms=transforms, rigidbodies=rigidbodies, bounds=bounds)

    def on_send(self, resp: List[bytes]) -> None:
        # This calls ObjectManager.on_send(resp) to update the transforms of each object.
        super().on_send(resp=resp)
        # Write the data to a JSON file. `self.transforms` is inherited from the parent `ObjectManager` class.
        data = dict()
        for object_id in self.transforms:
            o = self.transforms[object_id]
            data[object_id] = {"position": TDWUtils.array_to_vector3(o.position),
                               "rotation": TDWUtils.array_to_vector4(o.rotation)}
        # Get the file path using the frame coutner.
        path = self.output_directory.joinpath(str(self.frame).zfill(4) + ".json")
        # Serialize the data and write it to the file.
        path.write_text(json.dumps(data))
        # Increment the frame counter.
        self.frame += 1


if __name__ == "__main__":
    output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("custom_json")
    print(f"Output will be saved to: {output_directory}")
    # Create a controller.
    c = Controller()
    # Add the custom JSON writer.
    writer = ObjectDataWriter(output_directory=output_directory)
    c.add_ons.append(writer)
    # Create a scene with an object.
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   Controller.get_add_object(model_name="vase_02",
                                             position={"x": 1, "y": 0, "z": -2},
                                             rotation={"x": 0, "y": 30, "z": 0},
                                             object_id=0)])
    # Read the data.
    data_path = writer.output_directory.joinpath("0000.json")
    print(data_path.read_text())
    # End the simulation.
    c.communicate({"$type": "terminate"})
