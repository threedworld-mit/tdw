import json
from pkg_resources import resource_filename
from typing import Dict, List, Union
from pathlib import Path
from tdw.proc_gen.arrangements.cabinetry.cabinetry_type import CabinetryType


class _Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=_Decoder.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(dct):
        if "name" in dct:
            return Cabinetry(**dct)
        else:
            return {CabinetryType[k]: v for k, v in dct.items()}


class Cabinetry:
    """
    A set of cabinetry models.
    """

    def __init__(self, name: Union[str, CabinetryType], kitchen_counters: List[str], wall_cabinets: List[str],
                 sinks: List[str]):
        """
        :param name: The name of the cabinetry set.
        :param kitchen_counters: A list of names of kitchen counter models.
        :param wall_cabinets: A list of names of wall cabinet models.
        :param sinks: A list of names of kitchen sink models.
        """

        if isinstance(name, CabinetryType):
            """:field
            The name of the cabinetry set.
            """
            self.name: CabinetryType = name
        elif isinstance(name, str):
            self.name = CabinetryType[name]
        else:
            raise Exception(name)
        """:field
        A list of names of kitchen counter models.
        """
        self.kitchen_counters: List[str] = kitchen_counters
        """:field
        A list of names of wall cabinet models.
        """
        self.wall_cabinets: List[str] = wall_cabinets
        """:field
        A list of names of kitchen sink models.
        """
        self.sinks: List[str] = sinks


CABINETRY: Dict[CabinetryType, Cabinetry] = json.loads(Path(resource_filename(__name__, "cabinetry.json")).read_text(), cls=_Decoder)
