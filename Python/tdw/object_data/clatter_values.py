from tdw.physics_audio.impact_material import ImpactMaterial


class ClatterValues:
    """
    An object's Clatter audio values.
    """

    def __init__(self, impact_material: ImpactMaterial = ImpactMaterial.wood_medium, size: int = 3, amp: float = 0.2,
                 resonance: float = 0.05):
        """
        :param impact_material: The model's `ImpactMaterial`.
        :param size: The size bucket value (0-5).
        :param amp: The audio amplitude (0 to 1). This affects the overall loudness of audio generated by this object.
        :param resonance: The resonance value. This affects the decay times of audio generated by this object. The value is clamped to be at least 0 and usually should be below 1.
        """

        """:field
        The model's `ImpactMaterial`.
        """
        self.impact_material: ImpactMaterial = impact_material
        """:field
        The size bucket value (0-5).
        """
        self.size: int = size
        """:field
        The audio amplitude (0 to 1). This affects the overall loudness of audio generated by this object.
        """
        self.amp: float = amp
        """:field
        The resonance value. This affects the decay times of audio generated by this object. The value is clamped to be at least 0 and usually should be below 1.
        """
        self.resonance: float = resonance
