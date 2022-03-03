import json
from itertools import combinations
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import SceneLibrarian
from tdw.add_ons.object_manager import ObjectManager
from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.output_data import OutputData, ObjectColliderIntersection, EnvironmentColliderIntersection
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class ProcGenKitchenColliderIntersections(Controller):
    """
    Compute collider intersections between objects.
    """

    DISTANCE: float = 0.01
    SCENES = [r for r in SceneLibrarian().records if len(r.rooms) > 0]

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.object_manager = ObjectManager(transforms=True, rigidbodies=False, bounds=False)
        rng = np.random.RandomState()
        scene = ProcGenKitchenColliderIntersections.SCENES[rng.randint(0, len(ProcGenKitchenColliderIntersections.SCENES))]
        self.kitchen = ProcGenKitchen(scene=scene, rng=rng)
        self.composite_object_manager = CompositeObjectManager()
        self.add_ons.extend([self.kitchen, self.object_manager, self.composite_object_manager])
        self.path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_kitchen_collider_intersections")
        print(f"Data will be saved to: {self.path}")
        if not self.path.exists():
            self.path.mkdir(parents=True)

    def run(self) -> None:
        """
        Run 100 trials with fixed random seeds.
        """

        for i in range(1, 10):
            self.trial(random_seed=i)
        self.communicate({"$type": "terminate"})

    def trial(self, random_seed: int) -> None:
        """
        Run a trial. Create a scene.
        Get collider intersections between each pair of objects and between single objects and the environment.
        Print the results to the console and write them to disk as a .json file.

        :param random_seed: The random seed for the trial.
        """

        # Reset the kitchen.
        rng = np.random.RandomState(random_seed)
        scene = ProcGenKitchenColliderIntersections.SCENES[rng.randint(0, len(ProcGenKitchenColliderIntersections.SCENES))]
        self.kitchen.reset(scene=scene, rng=rng, create_scene=True)
        # Reset the object manager.
        self.object_manager.reset()
        self.composite_object_manager.reset()
        self.communicate([])
        # Get a list of object IDs.
        object_ids = list(self.object_manager.objects_static.keys())
        # Get the pairs of object IDs.
        # Source: https://stackoverflow.com/a/18201716
        object_id_pairs = [list(comb) for comb in combinations(object_ids, 2)]
        resp = self.communicate({"$type": "send_collider_intersections",
                                 "obj_intersection_ids": object_id_pairs,
                                 "env_intersection_ids": object_ids})
        # Record the intersections.
        data = {"random_seed": random_seed,
                "object_intersections": [],
                "environment_intersections": []}
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Object intersection.
            if r_id == "obci":
                obci = ObjectColliderIntersection(resp[i])
                distance = obci.get_distance()
                if distance < ProcGenKitchenColliderIntersections.DISTANCE:
                    continue
                object_id_a = obci.get_object_id_a()
                object_id_b = obci.get_object_id_b()
                # Ignore internal composite object collider intersections.
                if object_id_a in self.composite_object_manager.static and object_id_b in self.composite_object_manager.static[object_id_a].sub_object_ids:
                    continue
                if object_id_b in self.composite_object_manager.static and object_id_a in self.composite_object_manager.static[object_id_b].sub_object_ids:
                    continue
                # Record the collider intersection.
                data["object_intersections"].append({"object_id_a": object_id_a,
                                                     "object_name_a": self.object_manager.objects_static[object_id_a].name,
                                                     "object_position_a": TDWUtils.array_to_vector3(
                                                         self.object_manager.transforms[object_id_a].position),
                                                     "object_id_b": object_id_b,
                                                     "object_name_b": self.object_manager.objects_static[object_id_b].name,
                                                     "object_position_b": TDWUtils.array_to_vector3(
                                                         self.object_manager.transforms[object_id_b].position),
                                                     "distance": distance,
                                                     "direction": TDWUtils.array_to_vector3(obci.get_direction())})
            elif r_id == "enci":
                enci = EnvironmentColliderIntersection(resp[i])
                distance = enci.get_distance()
                if distance < ProcGenKitchenColliderIntersections.DISTANCE:
                    continue
                object_id = enci.get_object_id()
                data["environment_intersections"].append({"object_id": object_id,
                                                          "object_name": self.object_manager.objects_static[object_id].name,
                                                          "object_position": TDWUtils.array_to_vector3(
                                                              self.object_manager.transforms[object_id].position),
                                                          "distance": distance,
                                                          "direction": TDWUtils.array_to_vector3(enci.get_direction())})
        text = json.dumps(data, indent=2, sort_keys=True)
        print(random_seed, len(data["object_intersections"]), len(data["environment_intersections"]))
        # Dump the data.
        self.path.joinpath(str(random_seed) + ".json").write_text(text)


if __name__ == "__main__":
    c = ProcGenKitchenColliderIntersections(launch_build=False)
    c.run()
