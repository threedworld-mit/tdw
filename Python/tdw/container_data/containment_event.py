from tdw.container_data.container_collider_tag import ContainerColliderTag


class ContainmentEvent:
    """
    Data describing a containment event i.e. when a container's trigger colliders enter or stay with another object.
    """

    def __init__(self, container_id: int, object_id: int, tag: ContainerColliderTag):
        """
        :param container_id: The ID of the container.
        :param object_id: The ID of the contained object.
        :param tag: A semantic [`ContainerColliderTag`](container_collider_tag.md) describing the semantic nature of the event.
        """

        """:field
        The ID of the container.
        """
        self.container_id: int = container_id
        """:field
        The ID of the contained object.
        """
        self.object_id: int = object_id
        """:field
        A [`ContainerColliderTag`](container_collider_tag.md) describing the semantic nature of the event.
        """
        self.tag: ContainerColliderTag = tag

    def __eq__(self, other):
        if not isinstance(other, ContainmentEvent):
            return False
        return self.container_id == other.container_id and self.object_id == other.object_id and self.tag == other.tag

    def __hash__(self):
        return hash((self.container_id, self.object_id, self.tag.value))
