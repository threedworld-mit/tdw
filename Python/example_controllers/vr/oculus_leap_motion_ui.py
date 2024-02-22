from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion


class OculusLeapMotionUI(Controller):
    """
    Press 0 to make the cube red. Press 4 to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vr = OculusLeapMotion()
        self.cube_id: int = Controller.get_unique_id()
        self.vr.listen_to_button(button=0, callback=self.set_cube_color)
        self.add_ons.extend([self.vr])

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        z = 0.6
        commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 0, "z": z},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=self.cube_id,
                                                          position={"x": 0, "y": 1, "z": z - 0.25},
                                                          scale_mass=False,
                                                          scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                          default_physics_values=False,
                                                          mass=1,
                                                          library="models_flex.json"))
        self.communicate(commands)
        while not self.vr.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def set_cube_color(self) -> None:
        self.communicate({"$type": "set_color",
                          "id": self.cube_id,
                          "color": {"r": 1, "g": 0, "b": 0, "a": 1}})


if __name__ == "__main__":
    c = OculusLeapMotionUI()
    c.run()
