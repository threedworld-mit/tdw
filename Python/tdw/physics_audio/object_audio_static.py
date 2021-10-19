import io
from csv import DictReader
from pathlib import Path
from pkg_resources import resource_filename
from typing import Union, Dict
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


def get_static_audio_data(csv_file: Union[str, Path] = "") -> Dict[str, ObjectAudioStatic]:
    """
    Returns ObjectInfo values.
    As of right now, only a few objects in the TDW model libraries are included. More will be added in time.

    :param csv_file: The path to the .csv file containing the object info. By default, it will load `tdw/physics_audio/objects.csv`. If you want to make your own spreadsheet, use this file as a reference.

    :return: A list of default ObjectInfo. Key = the name of the model. Value = object info.
    """

    objects: Dict[str, ObjectAudioStatic] = {}
    # Load the objects.csv metadata file.
    if isinstance(csv_file, str):
        # Load the default file.
        if csv_file == "":
            csv_file = str(Path(resource_filename(__name__, f"objects.csv")).resolve())
        else:
            csv_file = str(Path(csv_file).resolve())
    else:
        csv_file = str(csv_file.resolve())

    # Parse the .csv file.
    with io.open(csv_file, newline='', encoding='utf-8-sig') as f:
        reader = DictReader(f)
        for row in reader:
            o = ObjectAudioStatic(name=row["name"], amp=float(row["amp"]), mass=float(row["mass"]),
                                  material=AudioMaterial[row["material"]], bounciness=float(row["bounciness"]),
                                  resonance=float(row["resonance"]), size=int(row["size"]), object_id=0)
            objects.update({o.name: o})
    return objects


DEFAULT_OBJECT_AUDIO_STATIC_DATA: Dict[str, ObjectAudioStatic] = get_static_audio_data()
