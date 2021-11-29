from typing import List, Tuple
from pathlib import Path
import json
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies


class Drop(Controller):
    """
    Drop an object and print its final position.
    """

    def trial(self, model_name: str, height: float) -> Tuple[float, float, float]:
        """
        Drop an object from a given height.

        :param model_name: The name of the model.
        :param height: The starting height of the model.

        :return: The final position of the object.
        """

        object_id = self.get_unique_id()
        # Add an object. Request Rigidbodies and Transforms output data.
        resp = self.communicate([c.get_add_object(model_name,
                                                  object_id=object_id,
                                                  position={"x": 0, "y": height, "z": 0}),
                                 {"$type": "send_rigidbodies",
                                  "frequency": "always"},
                                 {"$type": "send_transforms",
                                  "frequency": "always"}])
        # Call self.communicate() until the object is "sleeping" i.e. no longer moving.
        sleeping, object_position = Drop._get_object_state(resp=resp, object_id=object_id)
        while not sleeping:
            resp = self.communicate([])
            sleeping, object_position = Drop._get_object_state(resp=resp, object_id=object_id)
        # Destroy the object to reset the scene.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return object_position

    def run(self) -> None:
        # Load the trial data.
        trial_data = json.loads(Path("trials.json").read_text())
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))
        # Log the positions of the objects.
        positions = {}
        # Run a series of trials.
        for trial in trial_data["trials"]:
            model_name = trial["model_name"]
            height = trial["height"]
            position = self.trial(model_name=model_name, height=height)
            if model_name not in positions:
                positions[model_name] = []
            positions[model_name].append(position)
        print(positions)
        # End the simulation.
        self.communicate({"$type": "terminate"})

    @staticmethod
    def _get_object_state(resp: List[bytes], object_id: int) -> Tuple[bool, Tuple[float, float, float]]:
        """
        :param resp: The most recent response from the build.
        :param object_id: The object ID.

        :return: Tuple: True if the object is sleeping; The object's position as an (x, y, z) tuple.
        """

        sleeping = False
        object_position = (0, 0, 0)
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Parse Transforms output data to get the object's position.
            if r_id == "tran":
                transforms = Transforms(resp[i])
                for j in range(transforms.get_num()):
                    if transforms.get_id(j) == object_id:
                        object_position = transforms.get_position(j)
            # Parse Rigidbody data to determine if the object is sleeping.
            elif r_id == "rigi":
                rigidbodies = Rigidbodies(resp[i])
                for j in range(rigidbodies.get_num()):
                    if rigidbodies.get_id(j) == object_id:
                        sleeping = rigidbodies.get_sleeping(j)
        return sleeping, object_position


if __name__ == "__main__":
    c = Drop()
    c.run()
