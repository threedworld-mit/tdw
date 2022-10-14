from typing import List
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency
from tdw.output_data import OutputData, Containment


class Grasp(Action):
    """
    Grasp a target object.
    """

    def __init__(self, target: int, arm: Arm, dynamic: ReplicantDynamic):
        """
        :param target: The target object ID.
        :param arm: The [`Arm`](../../agents/arm.md) value for the hand that will grasp the target object.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data.
        """

        super().__init__()
        self._target: int = target
        self._arm: Arm = arm
        # We're already holding an object.
        if self._arm in dynamic.held_objects:
            self.status = ActionStatus.already_holding

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Get all of the objects contained by the grasped object. Parent them to the container and make them kinematic.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "cont":
                containment = Containment(resp[i])
                object_id = containment.get_object_id()
                if object_id == self._target:
                    overlap_ids = containment.get_overlap_ids()
                    for overlap_id in overlap_ids:
                        commands.extend([{"$type": "parent_object_to_object",
                                          "parent_id": self._target,
                                          "id": int(overlap_id)},
                                         {"$type": "set_kinematic_state",
                                          "id": int(overlap_id),
                                          "is_kinematic": True,
                                          "use_gravity": False}])
        # Grasp the object.
        commands.extend([{"$type": "replicant_grasp_object",
                          "id": static.replicant_id,
                          "arm": self._arm.name,
                          "object_id": self._target}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        self.status = ActionStatus.success
        return []
