import numpy as np
from tdw.container_data.container_tag import ContainerTag


class ContainmentEvent:
    """
    Data describing a containment event i.e. when a container shape overlaps with one or more objects.
    """

    def __init__(self, container_id: int, object_ids: np.array, tag: ContainerTag):
        """
        :param container_id: The ID of the container.
        :param object_ids: The IDs of the contained objects as a numpy array.
        :param tag: A semantic [`ContainerTag`](container_tag.md) describing the semantic nature of the event.
        """

        """:field
        The ID of the container.
        """
        self.container_id: int = container_id
        """:field
        The IDs of the contained objects as a numpy array
        """
        self.object_ids: np.array = object_ids
        """:field
        A semantic [`ContainerTag`](container_tag.md) describing the semantic nature of the event.
        """
        self.tag: ContainerTag = tag

    def __eq__(self, other):
        if not isinstance(other, ContainmentEvent):
            return False
        return self.container_id == other.container_id and self.tag == other.tag

    def __hash__(self):
        return hash((self.container_id, self.tag.value))
