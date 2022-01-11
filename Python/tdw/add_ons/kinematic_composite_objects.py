from typing import List
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, CompositeObjects


class KinematicCompositeObjects(AddOn):
    """
    A helper add-on for composite objects. Make all sub-objects with joints (hinges, motors, springs, and prismatic joints) non-kinematic.
    """

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_composite_objects"}]

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "comp":
                composite_objects = CompositeObjects(resp[i])
                for j in range(composite_objects.get_num()):
                    for k in range(composite_objects.get_num_sub_objects(j)):
                        machine_type = composite_objects.get_sub_object_machine_type(j, k)
                        if machine_type != "light" and machine_type != "none":
                            self.commands.append({"$type": "set_kinematic_state",
                                                  "id": composite_objects.get_sub_object_id(j, k),
                                                  "is_kinematic": False,
                                                  "use_gravity": True})
