from enum import Enum
from json import JSONEncoder


class TrialMessageEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.name
        return o.__dict__
