from tdw.obi_data.collision_materials.material_combine_mode import MaterialCombineMode


class CollisionMaterial:
    """
    Data for an Obi collision material.
    """

    def __init__(self, dynamic_friction: float = 0.3, static_friction: float = 0.3, stickiness: float = 0,
                 stick_distance: float = 0, friction_combine: MaterialCombineMode = MaterialCombineMode.average,
                 stickiness_combine: MaterialCombineMode = MaterialCombineMode.average):
        """
        :param dynamic_friction: Percentage of relative tangential velocity removed in a collision, once the static friction threshold has been surpassed and the particle is moving relative to the surface. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        :param static_friction: Percentage of relative tangential velocity removed in a collision. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        :param stickiness: Amount of inward normal force applied between objects in a collision. 0 means no force will be applied, 1 will keep objects from separating once they collide.
        :param stick_distance: Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated.
        :param friction_combine: A [`MaterialCombineMode`](material_combine_mode.md). How is the friction coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different friction combine modes, the mode with the lowest enum index is used.
        :param stickiness_combine: A [`MaterialCombineMode`](material_combine_mode.md). How is the stickiness coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different stickiness combine modes, the mode with the lowest enum index is used.
        """

        """:field
        Percentage of relative tangential velocity removed in a collision, once the static friction threshold has been surpassed and the particle is moving relative to the surface. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        """
        self.dynamic_friction: float = dynamic_friction
        """:field
        Percentage of relative tangential velocity removed in a collision. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        """
        self.static_friction: float = static_friction
        """:field
        Amount of inward normal force applied between objects in a collision. 0 means no force will be applied, 1 will keep objects from separating once they collide.
        """
        self.stickiness: float = stickiness
        """:field
        Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated.
        """
        self.stick_distance: float = stick_distance
        """:field
        A [`MaterialCombineMode`](material_combine_mode.md). How is the friction coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different friction combine modes, the mode with the lowest enum index is used.
        """
        self.friction_combine = friction_combine
        """:field
        A [`MaterialCombineMode`](material_combine_mode.md). How is the stickiness coefficient calculated when two objects involved in a collision have different coefficients. If both objects have different stickiness combine modes, the mode with the lowest enum index is used.
        """
        self.stickiness_combine = stickiness_combine

    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {k: v for k, v in self.__dict__.items()}
        d["friction_combine"] = d["friction_combine"].name
        d["stickiness_combine"] = d["stickiness_combine"].name
        return d
