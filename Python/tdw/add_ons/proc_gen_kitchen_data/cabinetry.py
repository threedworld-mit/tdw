import json
from pkg_resources import resource_filename
from typing import List
from pathlib import Path


class _Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=_Decoder.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(dct):
        return Cabinetry(**dct)


class Cabinetry:
    """
    A set of cabinetry models and materials.
    """

    def __init__(self, counter_models: List[str], wall_cabinet_models: List[str], sink_models: List[str],
                 counter_top_material: str):
        """
        :param counter_models: A list of names of kitchen counter models.
        :param wall_cabinet_models: A list of names of wall cabinet models.
        :param sink_models: A list of names of kitchen sink models.
        :param counter_top_material: The name of the kitchen countertop material.
        """

        """:field
        A list of names of kitchen counter models.
        """
        self.counter_models: List[str] = counter_models
        """:field
        A list of names of wall cabinet models.
        """
        self.wall_cabinet_models: List[str] = wall_cabinet_models
        """:field
        A list of names of kitchen sink models.
        """
        self.sink_models: List[str] = sink_models
        """:field
        The name of the kitchen countertop material.
        """
        self.counter_top_material: str = counter_top_material


CABINETRY: List[Cabinetry] = json.loads(Path(resource_filename(__name__, "cabinetry.json")).read_text(), cls=_Decoder)
