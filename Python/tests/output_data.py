from typing import List
import pytest
import numpy as np
from tdw.controller import Controller
from tdw.output_data import OutputData, AlbedoColors, Bounds, Categories, EulerAngles
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
    commands = [TDWUtils.create_empty_room(12, 12),
                {"$type": "simulate_physics",
                 "value": False}]
    cube_id = TestController.get_unique_id()
    cube_rotation = {"x": 30, "y": 15, "z": 0}
    commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                          object_id=cube_id,
                                                          position={"x": 0, "y": 1, "z": -2},
                                                          rotation=cube_rotation,
                                                          library="models_flex.json"))
    sphere_id = TestController.get_unique_id()
    sphere_rotation = {"x": 11, "y": 0, "z": 50}
    commands.extend(TestController.get_add_physics_object(model_name="sphere",
                                                          object_id=sphere_id,
                                                          position={"x": -2, "y": 0, "z": 3.1},
                                                          rotation=sphere_rotation,
                                                          library="models_flex.json"))
    object_ids = [cube_id, sphere_id]
    # Set the color.
    commands.extend([{"$type": "set_color",
                      "id": object_id,
                      "color": {"r": 1, "g": 1, "b": 1, "a": 1}} for object_id in object_ids])
    # Request output data.
    commands.extend([{"$type": "send_albedo_colors"},
                     {"$type": "send_bounds"},
                     {"$type": "send_categories"},
                     {"$type": "send_euler_angles"}])
    resp = controller.communicate(commands)
    albedo_colors = AlbedoColors(TestController.get_output_data(resp, "acol"))
    TestController.assert_num(albedo_colors)
    # Both objects are in the output data and have the correct color.
    for i in range(albedo_colors.get_num()):
        assert albedo_colors.get_id(i) in object_ids
        assert np.sum(albedo_colors.get_color(i).astype(int)) == 255 * 4
    # Test for expected bounds.
    bounds = Bounds(get_output_data(resp, "boun"))
    assert_num(bounds)
    extents = np.ones(shape=3)
    for index, object_id in zip([0, 1], object_ids):
        assert bounds.get_id(index) == object_id
        assert_arr(TDWUtils.get_bounds_extents(bounds, index), extents)
    # Test for expected categories.
    categories = Categories(get_output_data(resp, "cate"))
    assert categories.get_num_categories() == 1
    assert categories.get_category_name(0) == "flex_primitive"
    # Test Euler angles.
    euler_angles = EulerAngles(get_output_data(resp, "eule"))
    assert_num(euler_angles)
    for index, object_id, rotation in zip([0, 1], object_ids, [cube_rotation, sphere_rotation]):
        assert euler_angles.get_id(index) == object_id
        assert_arr(euler_angles.get_rotation(index), TDWUtils.vector3_to_array(rotation))


def get_output_data(resp: List[bytes], r_id: str) -> bytes:
    for i in range(len(resp) - 1):
        if r_id == OutputData.get_data_type_id(resp[i]):
            return resp[i]
    raise Exception(f"Output data {r_id} not found.")


def assert_num(output_data, expected_num: int = 2) -> None:
    assert output_data.get_num() == expected_num


def assert_arr(a: np.ndarray, b: np.ndarray, delta: float = 0.0001) -> None:
    assert a.shape == b.shape
    assert np.linalg.norm(a - b) <= delta


"""
AudioSourceDone
AudioSources
AvatarKinematic
AvatarNonKinematic
AvatarSegmentationColor
AvatarSimpleBody
AvatarTransformMatrices
CameraMatrices
Collision
Containment
Drones
DynamicCompositeObjects
DynamicEmptyObjects
DynamicRobots
EnvironmentColliderIntersection
EnvironmentCollision
FieldOfView
Framerate
IdPassGrayscale
IdPassSegmentationColors
Images
ImageSensors
IsOnNavMesh
Junk
Keyboard
Lights
LocalTransforms
LogMessage
Magnebot
MagnebotWheels
Meshes
Mouse
NavMeshPath
ObiParticles
ObjectColliderIntersection
Occlusion
OccupancyMap
OculusTouchButtons
Overlap
QuitSignal
Raycast
Replicants
ReplicantSegmentationColors
Rigidbodies
RobotJointVelocities
SceneRegions
ScreenPosition
SegmentationColors
StaticCompositeObjects
StaticEmptyObjects
StaticOculusTouch
StaticRigidbodies
StaticRobot
Substructure
TransformMatrices
Transforms
TriggerCollision
Version
Volumes
"""