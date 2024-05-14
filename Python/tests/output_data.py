import pytest
import numpy as np
from tdw.controller import Controller
from tdw.output_data import OutputData, AlbedoColors
from tdw.tdw_utils import TDWUtils
from test_controller import TestController


@pytest.fixture()
def controller(request):
    c = TestController()

    def teardown():
        c.communicate({"$type": "terminate"})
    request.addfinalizer(teardown)

    return c


def test_output_data(controller):
    assert isinstance(controller, TestController)
    # This should throw an exception.
    with pytest.raises(Exception) as _:
        controller.get_output_data([], "acol")
    commands = [TDWUtils.create_empty_room(12, 12)]
    cube_id = TestController.get_unique_id()
    commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                          object_id=cube_id,
                                                          position={"x": 0, "y": 1, "z": -2},
                                                          rotation={"x": 30, "y": 15, "z": 0},
                                                          library="models_flex.json"))
    sphere_id = TestController.get_unique_id()
    commands.extend(TestController.get_add_physics_object(model_name="sphere",
                                                          object_id=sphere_id,
                                                          position={"x": -2, "y": 0, "z": 3.1},
                                                          rotation={"x": 11, "y": 0, "z": 50},
                                                          library="models_flex.json"))
    object_ids = [cube_id, sphere_id]
    # Set the color.
    commands.extend([{"$type": "set_color",
                      "id": object_id,
                      "color": {"r": 1, "g": 1, "b": 1, "a": 1}} for object_id in object_ids])
    # Request output data.
    commands.extend([{"$type": "send_albedo_colors"},
                     {"$type": "send_bounds"}])
    resp = controller.communicate(commands)
    albedo_colors = AlbedoColors(controller.get_output_data(resp, "acol"))
    # Both objects are in the output data and have the correct color.
    num = albedo_colors.get_num()
    assert num == 2
    for i in range(num):
        assert albedo_colors.get_id(i) in object_ids
        assert np.sum(albedo_colors.get_color(i).astype(int)) == 255 * 4