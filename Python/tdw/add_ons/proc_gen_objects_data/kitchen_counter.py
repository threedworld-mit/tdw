from typing import Dict, List
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects_data.kitchen_cabinet import KitchenCabinet
from tdw.scene_data.region_walls import RegionWalls
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import ModelRecord


class KitchenCounter(KitchenCabinet):
    def __init__(self, record: ModelRecord, position: Dict[str, float], wall: CardinalDirection, region: InteriorRegion,
                 allow_microwave: bool):
        super().__init__(record=record, position=position, wall=wall, region=region)
        self._allow_microwave: bool = allow_microwave

    def get_commands(self) -> List[dict]:
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        # Place a microwave on top of the kitchen counter.
        if extents[0] < 0.7 and self._allow_microwave:
            root_object_id = Controller.get_unique_id()
            self.commands.extend(Controller.get_add_physics_object(model_name=record.name,
                                                                   object_id=root_object_id,
                                                                   position=kitchen_counter_position,
                                                                   rotation={"x": 0, "y": rotation, "z": 0},
                                                                   library="models_core.json",
                                                                   kinematic=True))
            # Get the top position of the kitchen counter.
            object_top = {"x": kitchen_counter_position["x"],
                          "y": record.bounds["top"]["y"] + kitchen_counter_position["y"],
                          "z": kitchen_counter_position["z"]}
            microwave_model_names = self.model_categories["microwave"]
            microwave_model_name = microwave_model_names[self.rng.randint(0, len(microwave_model_names))]
            microwave_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(microwave_model_name)
            # Add a microwave and add objects on top of the microwave.
            self.add_object_with_other_objects_on_top(record=microwave_record,
                                                      position=object_top,
                                                      rotation=rotation - 180,
                                                      category="microwave")
            self._used_unique_categories.append("microwave")
