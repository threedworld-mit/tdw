from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.logger import Logger
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.replicant.affordance_points import AffordancePoints
from tdw.replicant.image_frequency import ImageFrequency
import numpy as np

"""
Create a humanoid that walks across the room, knocks over a chair and reaches for 
a randomly-positioned object multiple times.
"""

class AvoidObstacles(Controller):

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate(TDWUtils.create_empty_room(12, 20))
        self.communicate(TDWUtils.create_avatar(position={"x": -0.5, "y": 1.175, "z": 6}, look_at={"x": 0.5, "y": 1, "z": 0}))

        self.replicant_id=self.get_unique_id()
        self.chair_id=self.get_unique_id()
        self.basket_id = self.get_unique_id()
        self.table_id = self.get_unique_id()
        self.ball_id = self.get_unique_id()
        self.ball_id2 = self.get_unique_id()

        self.replicant = Replicant(replicant_id=self.replicant_id, position={"x": 0, "y": 0, "z": -8}, image_frequency=ImageFrequency.never, avoid_objects=True)
        self.add_ons.append(self.replicant)
        commands=[]
        commands.extend([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                        self.get_add_object(model_name="chair_billiani_doll",
                                     object_id=self.chair_id,
                                     position={"x": 0, "y": 0, "z": 0},
                                     rotation={"x": 0, "y": 63.25, "z": 0}),
                        self.get_add_object(model_name="live_edge_coffee_table",
                                         object_id=self.table_id,
                                         position={"x": 1, "y": 0, "z": 2},
                                         rotation={"x": 0, "y": 20, "z": 0},
                                         library="models_core.json")])
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                               object_id=self.ball_id,
                               position={"x": 0, "y": 0, "z": 4.0},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                               object_id=self.ball_id2,
                               position={"x": 5, "y": 0, "z": 3.5},
                               rotation={"x": 0, "y": 0, "z": 0},
                               scale_factor={"x": 0.2, "y": 0.2, "z": 0.2},
                               kinematic=True,
                               gravity=False,
                               library="models_special.json"))
        self.communicate(commands)

    def run(self):
        self.replicant.collision_detection.objects = False
        #replicant.collision_detection.exclude_objects = [chair_id]
        while True:
            self.avoid_obstacles()


    def avoid_obstacles(self):
        self.replicant.move_to(target=self.ball_id, arrived_offset=0.2)
        while self.replicant.action.status == ActionStatus.ongoing:
                self.communicate([])
        if self.replicant.action.status == ActionStatus.detected_obstacle:
            print("Detected obstacle -- 1")
            self.replicant.turn_by(angle=45.0)
            while self.replicant.action.status == ActionStatus.ongoing:
                self.communicate([])
            self.replicant.move_by(distance=1.0)
            while self.replicant.action.status == ActionStatus.ongoing:
                self.communicate([])
            return
                   

if __name__ == "__main__":
    AvoidObstacles(launch_build=False).run()


