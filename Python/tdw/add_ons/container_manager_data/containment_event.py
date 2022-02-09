from tdw.add_ons.container_manager_data.container_collider_tag import ContainerColliderTag


class ContainmentEvent:
    """
    Data describing a containment event i.e. when a container's trigger colliders enter or stay with another object.
    """

    def __init__(self, container_id: int, object_id: int, tag: ContainerColliderTag):
        """
        :param container_id: The ID of the container.
        :param object_id: The ID of the contained object.
        :param tag: A [`ContainerColliderTag`](container_collider_tag.md) describing the semantic nature of the event.
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