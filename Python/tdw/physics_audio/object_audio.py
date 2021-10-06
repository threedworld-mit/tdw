from tdw.physics_audio.audio_material import AudioMaterial


class ObjectAudio:
    """
    Impact sound data for an object in a TDW model library.
    The audio values here are just recommendations; you can apply different values if you want.
    """

    def __init__(self, name: str, amp: float, mass: float, material: AudioMaterial, library: str, bounciness: float, resonance: float, size: int):
        """
        :param name: The model name.
        :param amp: The sound amplitude.
        :param mass: The object mass.
        :param material: The audio material.
        :param library: The path to the model library (see ModelLibrarian documentation).
        :param bounciness: The bounciness value for a Unity physics material.
        :param resonance: The resonance value for the object.
        :param size: Integer representing the size "bucket" this object belongs to (0-5).
        """

        self.amp = amp
        self.library = library
        self.mass = mass
        self.material = material
        self.name = name
        self.bounciness = bounciness
        self.resonance = resonance
        self.size = size
