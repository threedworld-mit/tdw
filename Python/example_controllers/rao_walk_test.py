from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.add_ons.replicant import Replicant
from tdw.output_data import OutputData, Transforms
from random import uniform
from time import sleep
import os
from math import ceil
import numpy as np


"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""


class RelicantWalk(Controller):
    def run(self):
        replicant = Replicant(replicant_id=self.get_unique_id())
        self.add_ons.append(replicant)
        resp = self.communicate([TDWUtils.create_empty_room(12, 12),
                                 TDWUtils.create_avatar(position={"x": -4.42, "y": 1.5, "z": 5.95}, look_at={"x": 0, "y": 1.0, "z": -3})])
        
        replicant.move_by(distance=8)
        while replicant.action.status == ActionStatus.ongoing:
            self.communicate([])

if __name__ == "__main__":
    RelicantWalk(launch_build=False).run()
