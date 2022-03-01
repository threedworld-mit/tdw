from abc import ABC, abstractmethod
from typing import Dict
from tdw.container_data.container_collider_tag import ContainerColliderTag
from tdw.collision_data.trigger_collider_shape import TriggerColliderShape


class ContainerTriggerCollider(ABC):
    """
    Data for a container trigger collider.
    """

    def __init__(self, tag: ContainerColliderTag, position: Dict[str, float]):
        """
        :param tag: The collider's semantic [`ContainerColliderTag`](container_collider_tag.md).
        :param position: The local position of the collider.
        """

        """:field
        The collider's semantic [`ContainerColliderTag`](container_collider_tag.md).
        """
        self.tag: ContainerColliderTag = tag
        """:field
        The collider's local position.
        """
        self.position: Dict[str, float] = {"x": round(position["x"], 8),
                                           "y": round(position["y"], 8),
                                           "z": round(position["z"], 8)}
        """:field
        The [`TriggerColliderShape`](../collision_data/trigger_collider_shape.md).
        """
        self.shape: TriggerColliderShape = self._get_shape()
        """:field
        The bottom-center position of the collider. Unlike TDW objects, the true pivot of a trigger collider is at its centroid.
        """
        self.bottom_center_position = {"x": self.position["x"], "y": self._get_bottom_y(), "z": self.position["z"]}

    @abstractmethod
    def _get_shape(self) -> TriggerColliderShape:
        """
        :return: The shape of the collider.
        """

        raise Exception()

    @abstractmethod
    def _get_bottom_y(self) -> float:
        """
        :return: The bottom y positional coordinate of the collider. The collider's true pivot is always at its centroid.
        """

        raise Exception
