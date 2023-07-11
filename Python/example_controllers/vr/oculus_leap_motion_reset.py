from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion


class OculusLeapMotionResetScene(Controller):
    """
    Press 0 to reset the scene. Press 4 to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.vr = OculusLeapMotion()
        self.vr.listen_to_button(button=0, callback=self.reset_scene)
        self.add_ons.extend([self.vr])

    def run(self) -> None:
        self.reset_scene()
        while not self.vr.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def reset_scene(self) -> None:
        self.vr.reset()
        commands = [{"$type": "load_scene",
                     "scene_name": "ProcGenScene"},
                    TDWUtils.create_empty_room(12, 12)]
        z = 0.6
        commands.extend(Controller.get_add_physics_object(model_name="small_table_green_marble",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 0, "z": z},
                                                          kinematic=True))
        commands.extend(Controller.get_add_physics_object(model_name="cube",
                                                          object_id=Controller.get_unique_id(),
                                                          position={"x": 0, "y": 1, "z": z - 0.25},
                                                          scale_mass=False,
                                                          scale_factor={"x": 0.05, "y": 0.05, "z": 0.05},
                                                          default_physics_values=False,
                                                          mass=1,
                                                          library="models_flex.json"))
        self.communicate(commands)


if __name__ == "__main__":
    c = OculusLeapMotionResetScene()
    c.run()
