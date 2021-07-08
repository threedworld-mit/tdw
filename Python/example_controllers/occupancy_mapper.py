from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.occupancy_map import OccupancyMap
from tdw.add_ons.third_person_camera import ThirdPersonCamera


class OccupancyMapper(Controller):
    def run(self) -> None:
        self.start()
        o = OccupancyMap()
        self.add_ons.append(o)
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_object(model_name="rh10",
                                              position={"x": 1, "y": 0, "z": -3.6},
                                              object_id=self.get_unique_id()),
                         self.get_add_object(model_name="trunck",
                                             position={"x": 4, "y": 0, "z": 1.3},
                                             rotation={"x": 0, "y": -28, "z": 0},
                                             object_id=self.get_unique_id())])
        o.generate()
        self.communicate([])
        cam = ThirdPersonCamera(position={"x": 0, "y": 14, "z": 0},
                                look_at=TDWUtils.VECTOR3_ZERO)
        self.add_ons.append(cam)
        o.show()
        self.communicate([])
        #self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = OccupancyMapper(launch_build=False)
    c.run()