from typing import List, Dict
from tdw.output_data import OutputData, Replicants
from tdw.object_data.transform import Transform
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.agent_data.agent_dynamic import AgentDynamic


class ReplicantDynamic(AgentDynamic):
    """
    Dynamic data for a Replicant that can change per `communicate()` call (such as the position of the Replicant).
    """

    def __init__(self, resp: List[bytes], replicant_id: int, frame_count: int):
        """
        :param resp: The response from the build, which we assume contains `replicant` output data.
        :param replicant_id: The ID of this replicant.
        :param frame_count: The current frame count.
        """

        super().__init__(resp=resp, agent_id=replicant_id, frame_count=frame_count)

        """:field
        A dictionary of objects held in each hand. Key = [`Arm`](arm.md). Value = Object ID.
        """
        self.held_objects: Dict[Arm, int] = dict()
        # File extensions per pass.
        self.__image_extensions: Dict[str, str] = dict()
        """:field
        Transform data for each body part. Key = Body part ID. Value = [`Transform`](../object_data/transform.md).
        """
        self.body_parts: Dict[int, Transform] = dict()
        """:field
        Collision data per body part. Key = Body part ID. Value = A list of object IDs that the body part collided with.
        """
        self.collisions: Dict[int, List[int]] = dict()
        """:field
        This is meant for internal use only. For certain actions, the build will update the Replicant's `ActionStatus`. *Do not use this field to check the Replicant's status.* Always check `replicant.action.status` instead. 
        """
        self.output_data_status: ActionStatus = ActionStatus.ongoing
        self._frame_count: int = frame_count
        got_data = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Get replicant's data.
            if r_id == "repl":
                replicants = Replicants(resp[i])
                for j in range(replicants.get_num()):
                    object_id = replicants.get_id(j)
                    # We found the ID of this replicant.
                    if object_id == replicant_id:
                        # Get the held objects.
                        if replicants.get_is_holding_left(j):
                            self.held_objects[Arm.left] = replicants.get_held_left(j)
                        if replicants.get_is_holding_right(j):
                            self.held_objects[Arm.right] = replicants.get_held_right(j)
                        # Get the body part transforms.
                        num_body_parts = replicants.get_num_body_parts()
                        for k in range(num_body_parts - 1):
                            # Cache the transform.
                            body_part_id = replicants.get_body_part_id(j, k)
                            self.body_parts[body_part_id] = Transform(position=replicants.get_body_part_position(j, k),
                                                                      forward=replicants.get_body_part_forward(j, k),
                                                                      rotation=replicants.get_body_part_rotation(j, k))
                            # Get collisions.
                            self.collisions[body_part_id] = list()
                            for m in range(10):
                                if replicants.get_is_collision(j, k, m):
                                    self.collisions[body_part_id].append(replicants.get_collision_id(j, k, m))
                        self.transform = Transform(position=replicants.get_position(j),
                                                   rotation=replicants.get_rotation(j),
                                                   forward=replicants.get_forward(j))
                        self.output_data_status = replicants.get_status(j)
                        # Get collision data.
                        got_data = True
                        break
            if got_data:
                break

    def get_collision_enters(self, collision_detection: CollisionDetection) -> List[int]:
        """
        :param collision_detection: The [`CollisionDetection`](collision_detection.md) rules.

        :return: A list of body IDs that entered a collision on this frame, filtered by the collision detection rules.
        """

        if not collision_detection.objects:
            return []
        enters: List[int] = list()
        for body_part_id in self.collisions:
            if body_part_id not in self.body_parts:
                continue
            for object_id in self.collisions[body_part_id]:
                if object_id in collision_detection.exclude_objects or object_id in self.body_parts:
                    continue
                # Ignore held objects.
                if collision_detection.held and (
                        (Arm.left in self.held_objects and self.held_objects[Arm.left] == object_id) or
                        (Arm.right in self.held_objects and self.held_objects[Arm.right] == object_id)):
                    continue
                enters.append(object_id)
        return enters

