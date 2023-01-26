from tdw.controller import Controller
from tdw.add_ons.proc_gen_kitchen import ProcGenKitchen
from tdw.add_ons.occupancy_map import OccupancyMap
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion



class OculusTouchProcGen(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.kitchen: ProcGenKitchen = ProcGenKitchen()
        self.occupancy_map: OccupancyMap = OccupancyMap(cell_size=0.7)
        self.vr = OculusLeapMotion(attach_avatar=False, set_graspable=True)
        self.done: bool = False
        self.add_ons.extend([self.kitchen,
                             self.occupancy_map,
                             self.vr])
        self.next_trial()

    def run(self) -> None:
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self) -> None:
        self.done = True

    def next_trial(self) -> None:
        # Show the loading screen.
        self.vr.show_loading_screen(show=True)
        self.communicate({"$type": "create_empty_environment"})
        # Reset the scene.
        self.kitchen.create()
        self.occupancy_map.reset()
        self.vr.reset()
        self.communicate([])
        # Generate the occupancy map.
        self.occupancy_map.generate()
        self.communicate([])
        # Get an unoccupied position.
        rig_position = {"x": 0, "y": 0, "z": 0}
        for ix in range(self.occupancy_map.occupancy_map.shape[0]):
            for iy in range(self.occupancy_map.occupancy_map.shape[1]):
                if self.occupancy_map.occupancy_map[ix][iy] == 0:
                    x, z = self.occupancy_map.get_occupancy_position(ix, iy)
                    rig_position = {"x": float(x), "y": 0, "z": float(z)}
                    break
        # Set the position of the rig and hide the loading screen.
        self.vr.set_position(rig_position)
        self.vr.show_loading_screen(show=False)


if __name__ == "__main__":
    c = OculusTouchProcGen()
    c.run()