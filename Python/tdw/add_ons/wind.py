from typing import Dict, List
from tdw.add_ons.add_on import AddOn
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.wind_source import WindSource


class Wind(AddOn):
    def __init__(self):
        super().__init__()
        self.wind_sources: Dict[int, WindSource] = dict()

    def on_send(self, resp: List[bytes]) -> None:
        # Update each wind source.
        for wind_id in self.wind_sources:
            self.commands.extend(self.wind_sources[wind_id].update())
