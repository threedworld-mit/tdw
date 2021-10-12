from tdw.physics_audio.audio_material import AudioMaterial


class ObjectAudioStatic:
    """
    Impact sound data for an object in a TDW model library.
    The audio values here are just recommendations; you can apply different values if you want.
    """

    def __init__(self, name: str, amp: float, mass: float, material: AudioMaterial, bounciness: float, resonance: float, size: int, object_id: int):
        """
        :param name: The model name.
        :param amp: The sound amplitude.
        :param mass: The object mass.
        :param material: The audio material.
        :param bounciness: The bounciness value for a Unity physics material.
        :param resonance: The resonance value for the object.
        :param size: Integer representing the size "bucket" this object belongs to (0-5).
        :param object_id: The ID of the object.
        """

        """:field
        The sound amplitude.
        """
        self.amp: float = amp
        """:float
        The object mass.
        """
        self.mass: float = mass
        """:field
        The audio material.
        """
        self.material: AudioMaterial = material
        """:field
        The name of the object.
        """
        self.name: str = name
        """:field
        The bounciness value for a Unity physics material. 
        """
        self.bounciness: float = bounciness
        """:field
        The resonance value for the object.
        """
        self.resonance: float = resonance
        """:field
        Integer representing the size "bucket" this object belongs to (0-5).
        """
        self.size = size
        """:field
        The ID of the object.
        """
        self.object_id = object_id
