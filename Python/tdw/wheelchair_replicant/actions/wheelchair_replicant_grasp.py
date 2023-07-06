from typing import List
from tdw.replicant.actions.grasp import Grasp
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic


class WheelchairReplicantGrasp(Grasp):
    """
    Grasp a target object.

    The action fails if the hand is already holding an object. Otherwise, the action succeeds.

    When an object is grasped, it is made kinematic. Any objects contained by the object are parented to it and also made kinematic. For more information regarding containment in TDW, [read this](../../../lessons/semantic_states/containment.md).
    """

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Ignore collisions.
        for object_id in self._grasping_ids:
            commands.append({"$type": "ignore_collisions",
                             "id": object_id,
                             "other_id": static.replicant_id,
                             "ignore": True})
        return commands
