import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vive_pro_eye import ViveProEye


class ViveProEyeOutputData(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.color = {"r": 0, "g": 0, "b": 1, "a": 1}
        self.color_delta = 0.01
        self.object_id = Controller.get_unique_id()
        self.vr = ViveProEye()
        self.vr.listen_to_axis(is_left=True, function=self.left_axis)
        self.vr.listen_to_axis(is_left=False, function=self.right_axis)
        self.add_ons.append(self.vr)

    def left_axis(self, axis: np.ndarray):
        if axis[0] > 0:
            self.color_up("r")
        elif axis[0] < 0:
            self.color_down("r")
        if axis[1] > 0:
            self.color_up("g")
        elif axis[1] < 0:
            self.color_down("g")

    def right_axis(self, axis: np.ndarray):
        if axis[0] > 0:
            self.color_up("b")
        elif axis[0] < 0:
            self.color_down("b")
        if axis[1] > 0:
            self.color_up("a")
        elif axis[1] < 0:
            self.color_down("a")

    def color_up(self, channel: str):
        self.color[channel] += self.color_delta
        if self.color[channel] > 1:
            self.color[channel] = 1

    def color_down(self, channel: str):
        self.color[channel] -= self.color_delta
        if self.color[channel] < 0:
            self.color[channel] = 0

    def run(self):
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          Controller.get_add_object(model_name="cube",
                                                    library="models_flex.json",
                                                    object_id=self.object_id,
                                                    position={"x": 0, "y": 0, "z": 0.5}),
                          {"$type": "scale_object",
                           "id": self.object_id,
                           "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2}}])
        while True:
            # Set the color of the cube.
            self.communicate([{"$type": "set_color",
                               "id": self.object_id,
                               "color": self.color}])


if __name__ == "__main__":
    c = ViveProEyeOutputData()
    c.run()
