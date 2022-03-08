import json
from pkg_resources import resource_filename
from typing import Dict, List, Union
from pathlib import Path
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_type import KitchenCabinetType


class _Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=_Decoder.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(dct):
        if "name" in dct:
            return KitchenCabinetSet(**dct)
        else:
            return {KitchenCabinetType[k]: v for k, v in dct.items()}


class KitchenCabinetSet:
    """
    A set of cabinetry models and materials.
    """

    def __init__(self, name: Union[str, KitchenCabinetType], kitchen_counters: List[str], wall_cabinets: List[str],
                 sinks: List[str], counter_top_material: str):
        """
        :param name: The name of the cabinetry set.
        :param kitchen_counters: A list of names of kitchen counter models.
        :param wall_cabinets: A list of names of wall cabinet models.
        :param sinks: A list of names of kitchen sink models.
        :param counter_top_material: The name of the kitchen countertop material.
        """

        if isinstance(name, KitchenCabinetType):
            """:field
            The name of the cabinetry set.
            """
            self.name: KitchenCabinetType = name
        elif isinstance(name, str):
            self.name = KitchenCabinetType[name]
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
        """:field
        The name of the kitchen countertop material.
        """
        self.counter_top_material: str = counter_top_material


CABINETRY: Dict[KitchenCabinetType, KitchenCabinetSet] = json.loads(Path(resource_filename(__name__, "kitchen_cabinets.json")).read_text(), cls=_Decoder)
