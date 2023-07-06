from typing import List
from tdw.output_data import OutputData, Containment, Replicants
from tdw.replicant.actions.drop import Drop
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic


class WheelchairReplicantDrop(Drop):
    """
    Drop a held object.

    The action ends when the object stops moving or the number of consecutive `communicate()` calls since dropping the object exceeds `self.max_num_frames`.

    When an object is dropped, it is made non-kinematic. Any objects contained by the object are parented to it and also made non-kinematic. For more information regarding containment in TDW, [read this](../../../lessons/semantic_states/containment.md).
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Stop ignoring collisions with the held object.
        commands.append({"$type": "ignore_collisions",
                         "id": self.object_id,
                         "other_id": static.replicant_id,
                         "ignore": False})
        # Stop ignoring collisions with the contained objects.
        replicant_ids: List[int] = list()
        # Get all Replicant IDs.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    replicant_ids.append(replicants.get_id(j))
                break
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "cont":
                containment = Containment(resp[i])
                object_id = containment.get_object_id()
                if object_id == self.object_id:
                    overlap_ids = containment.get_overlap_ids()
                    # Ignore Replicants.
                    overlap_ids = [o_id for o_id in overlap_ids if o_id not in replicant_ids]
                    for overlap_id in overlap_ids:
                        child_id = int(overlap_id)
                        commands.append({"$type": "ignore_collisions",
                                         "id": child_id,
                                         "other_id": static.replicant_id,
                                         "ignore": False})
        return commands
