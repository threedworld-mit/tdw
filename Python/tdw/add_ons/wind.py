from typing import Dict
from tdw.add_ons.add_on import AddOn
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.wind_source import WindSource

# radius_scale
#

class Wind(AddOn):
    def __init__(self):
        super().__init__()
        self.wind_sources: Dict[int, WindSource] = dict()

    def add_source(self, wind_id: int, visible: bool = False):
        fluid = Fluid(capacity=1000,
                      color={"r": 0, "g": 0, "b": 1, "a": 1},
                      transparency=1 if visible else 0,
                      thickness_cutoff=1 if visible else 100,
                      viscosity=0,
                      reflection=0,
                      refraction=0,
                      rest_density=1.293,
                      diffusion=0,
                      atmospheric_drag=0,
                      atmospheric_pressure=0,
                      particle_z_write=False,
                      thickness_downsample=2,
                      radius_scale=1,
                      render_smoothness=1,
                      absorption=0,
                      surface_tension=0)

    def set_gustiness(self, wind_id: int, capacity: Tuple[int, int] = None):
        """
        Set the "gustiness" of a wind source i.e. whether the wind should
        :param wind_id: The ID of the wind source.
        :param capacity:
        :return:
        """
