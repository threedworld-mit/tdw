from typing import List, Optional
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency
from tdw.output_data import OutputData, Containment, Replicants


class Grasp(Action):
    """
    Grasp a target object.

    The action fails if the hand is already holding an object. Otherwise, the action succeeds.

    When an object is grasped, it is made kinematic. Any objects contained by the object are parented to it and also made kinematic. For more information regarding containment in TDW, [read this](../../../lessons/semantic_states/containment.md).
    """

    def __init__(self, target: int, arm: Arm, dynamic: ReplicantDynamic, angle: Optional[float], axis: Optional[str],
                 relative_to_hand: bool, offset: float):
        """
        :param target: The target object ID.
        :param arm: The [`Arm`](../arm.md) value for the hand that will grasp the target object.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param angle: Continuously (per `communicate()` call, including after this action ends), rotate the the grasped object by this many degrees relative to the hand. If None, the grasped object will maintain its initial rotation.
        :param axis: Continuously (per `communicate()` call, including after this action ends) rotate the grasped object around this axis relative to the hand. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation.
        :param relative_to_hand: If True, the object rotates relative to the hand holding it. If False, the object rotates relative to the Replicant. Ignored if `angle` or `axis` is None.
        :param offset: Offset the object's position from the Replicant's hand by this distance.
        """

        super().__init__()
        """:field
        The target object ID.
        """
        self.target: int = target
        """:field
        The [`Arm`](../arm.md) value for the hand that will grasp the target object.
        """
        self.arm: Arm = arm
        """:field
        Continuously (per `communicate()` call, including after this action ends), rotate the grasped object by this many degrees. If None, the grasped object will maintain its initial rotation.
        """
        self.angle: Optional[float] = angle
        """:field
        Continuously (per `communicate()` call, including after this action ends), rotate the grasped object around this axis. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation.
        """
        self.axis: Optional[str] = axis
        """:field
        If True, the object rotates relative to the hand holding it. If False, the object rotates relative to the Replicant. Ignored if `angle` or `axis` is None.
        """
        self.relative_to_hand: bool = relative_to_hand
        """:field
        Offset the object's position from the Replicant's hand by this distance.
        """
        self.offset: float = offset
        # We're already holding an object.
        if self.arm in dynamic.held_objects:
            self.status = ActionStatus.already_holding

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        replicant_ids: List[int] = list()
        # Get all Replicant IDs.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    replicant_ids.append(replicants.get_id(j))
                break
        grasping_ids: List[int] = [self.target]
        # Get all of the objects contained by the grasped object. Parent them to the container and make them kinematic.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "cont":
                containment = Containment(resp[i])
                object_id = containment.get_object_id()
                if object_id == self.target:
                    overlap_ids = containment.get_overlap_ids()
                    # Ignore Replicants.
                    overlap_ids = [o_id for o_id in overlap_ids if o_id not in replicant_ids]
                    for overlap_id in overlap_ids:
                        child_id = int(overlap_id)
                        commands.extend([{"$type": "parent_object_to_object",
                                          "parent_id": self.target,
                                          "id": child_id},
                                         {"$type": "set_kinematic_state",
                                          "id": child_id,
                                          "is_kinematic": True,
                                          "use_gravity": False}])
                        grasping_ids.append(child_id)
        # Grasp the object. Disable the NavMeshObstacle, if any.
        commands.extend([{"$type": "replicant_grasp_object",
                         "id": static.replicant_id,
                          "arm": self.arm.name,
                          "object_id": self.target,
                          "offset": self.offset},
                         {"$type": "enable_nav_mesh_obstacle",
                          "id": self.target,
                          "enable": False}])
        # Set the object's rotation.
        if self.angle is not None and self.axis is not None:
            commands.append({"$type": "replicant_set_grasped_object_rotation",
                             "id": static.replicant_id,
                             "arm": self.arm.name,
                             "angle": self.angle,
                             "axis": self.axis,
                             "relative_to_hand": self.relative_to_hand})
        # Ignore collisions.
        for object_id in grasping_ids:
            commands.append({"$type": "ignore_collisions",
                             "id": object_id,
                             "other_id": static.replicant_id,
                             "ignore": True})
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # The build might've signaled that the action ended in failure.
        if dynamic.output_data_status != ActionStatus.ongoing:
            self.status = dynamic.output_data_status
        # If the build didn't signal anything, assume that we grasped the object.
        else:
            self.status = ActionStatus.success
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
