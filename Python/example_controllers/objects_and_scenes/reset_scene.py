import numpy as np
from tdw.controller import Controller
from tdw.output_data import OutputData, Rigidbodies


class ResetScene(Controller):
    """
    Create multiple trials of an object falling and reset the scene between trials.
    """

    def __init__(self, port: int = 1071, launch_build: bool = True, random_seed: int = 0):
        super().__init__(port=port, launch_build=launch_build)
        self.rng: np.random.RandomState = np.random.RandomState(random_seed)

    def do_trials(self, num_trials: int):
        scenes = ["tdw_room", "iceland_beach", "lava_field", "abandoned_factory"]
        # Divided the total number of trials by the number of scenes.
        num_trials_per_scene = int(num_trials / len(scenes))
        # Initialize a scene for the next batch of trials.
        for scene in scenes:
            self.communicate(self.get_add_scene(scene_name=scene))
            # Do trials for this scene.
            self.do_trials_in_scene(num_trials=num_trials_per_scene)
        self.communicate({"$type": "terminate"})

    def do_trials_in_scene(self, num_trials: int):
        for i in range(num_trials):
            # Add an object with a random rotation and starting height.
            object_id = self.get_unique_id()
            resp = self.communicate([self.get_add_object(model_name="rh10",
                                                         position={"x": 0, "y": self.rng.uniform(1.6, 3), "z": 0},
                                                         rotation={"x": self.rng.uniform(-360, 360),
                                                                   "y": self.rng.uniform(-360, 360),
                                                                   "z": self.rng.uniform(-360, 360)},
                                                         object_id=object_id),
                                     {"$type": "send_rigidbodies",
                                      "frequency": "always"}])

            done = False
            while not done:
                # Check if the object stopped moving.
                for j in range(len(resp) - 1):
                    r_id = OutputData.get_data_type_id(resp[j])
                    if r_id == "rigi":
                        rigidbodies = Rigidbodies(resp[j])
                        for k in range(rigidbodies.get_num()):
                            if rigidbodies.get_id(k) == object_id:
                                done = rigidbodies.get_sleeping(k)
                # Advance another frame.
                resp = self.communicate([])

            # Reset the scene by destroying the object.
            self.communicate([{"$type": "destroy_object",
                               "id": object_id},
                              {"$type": "send_rigidbodies",
                               "frequency": "never"}])


if __name__ == "__main__":
    c = ResetScene()
    c.do_trials(num_trials=10000)