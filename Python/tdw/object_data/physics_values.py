class PhysicsValues:
    """
    Physics values for an object. This is used in CommandHelpers.AddObject().
    """

    def __init__(self, mass: float = 1, dynamic_friction: float = 0.3, static_friction: float = 0.3, bounciness: float = 0.7):
        """
        :param mass: The mass of the object in kg.
        :param dynamic_friction: Friction when the object is already moving. A higher value means that the object will come to rest very quickly. Must be between 0 and 1.
        :param static_friction: Friction when the object is not moving. A higher value means that a lot of force will be needed to make the object start moving. Must be between 0 and 1.
        :param bounciness: The bounciness of the object. A higher value means that the object will bounce without losing much energy. Must be between 0 and 1.
        """

        """:field
        The mass of the object in kg.
        """
        self.mass: float = mass
        """:field
        Friction when the object is already moving. A higher value means that the object will come to rest very quickly. Must be between 0 and 1.
        """
        self.dynamic_friction: float = dynamic_friction
        """:field
        Friction when the object is not moving. A higher value means that a lot of force will be needed to make the object start moving. Must be between 0 and 1.
        """
        self.static_friction: float = static_friction
        """:field
        The bounciness of the object. A higher value means that the object will bounce without losing much energy. Must be between 0 and 1.
        """
        self.bounciness: float = bounciness
