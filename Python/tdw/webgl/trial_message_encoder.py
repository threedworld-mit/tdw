import re
from enum import Enum
from json import JSONEncoder
from tdw.webgl.trials.trial import Trial
from tdw.webgl.trial_adders.trial_adder import TrialAdder


class TrialMessageEncoder(JSONEncoder):
    """
    JSON encoder for a `TrialMessage`.
    """

    _CAMEL_CASE_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')

    def default(self, o):
        if isinstance(o, Enum):
            return o.name
        elif isinstance(o, Trial):
            d = TrialMessageEncoder._get_dict_with_type(o)
            return d
        elif isinstance(o, TrialAdder):
            return TrialMessageEncoder._get_dict_with_type(o)
        return o.__dict__

    @staticmethod
    def _get_dict_with_type(o):
        d = {"$type": TrialMessageEncoder._CAMEL_CASE_PATTERN.sub('_', o.__class__.__name__).lower()}
        d.update(o.__dict__)
        return d
