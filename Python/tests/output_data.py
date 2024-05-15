from typing import List, Union, Dict
import pytest
import numpy as np
from tdw.output_data import (OutputData, AlbedoColors, Bounds, Categories, Collision, EnvironmentCollision, EulerAngles,
                             LocalTransforms, Meshes, QuitSignal, Rigidbodies, SegmentationColors, StaticRigidbodies,
                             Substructure, Volumes, Transforms)
from tdw.tdw_utils import TDWUtils
from tdw.quaternion_utils import QuaternionUtils
from test_controller import TestController


@pytest.fixture()
def controller(request):
    c = TestController()

    def teardown():
        resp = c.communicate({"$type": "terminate"})
        assert QuitSignal(get_output_data(resp, "quit")).get_ok()
    request.addfinalizer(teardown)

    return c


def test_object_output_data(controller):
    assert isinstance(controller, TestController)
    # This should throw an exception.
    with pytest.raises(Exception) as _:
        get_output_data([], "acol")
    commands = [TDWUtils.create_empty_room(12, 12),
                {"$type": "simulate_physics",
                 "value": False}]
    cube_id = TestController.get_unique_id()
    cube_position = {"x": 0, "y": 1, "z": -2}
    cube_rotation = {"x": 30, "y": 15, "z": 0}
    commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                          object_id=cube_id,
                                                          position=cube_position,
                                                          rotation=cube_rotation,
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          static_friction=0.7,
                                                          dynamic_friction=0.7,
                                                          bounciness=0.3,
                                                          mass=3))
    sphere_id = TestController.get_unique_id()
    sphere_position = {"x": -2, "y": 0, "z": 3.1}
    sphere_rotation = {"x": 11, "y": 0, "z": 50}
    commands.extend(TestController.get_add_physics_object(model_name="sphere",
                                                          object_id=sphere_id,
                                                          position=sphere_position,
                                                          rotation=sphere_rotation,
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          static_friction=0.7,
                                                          dynamic_friction=0.7,
                                                          bounciness=0.3,
                                                          mass=3))
    object_ids = [cube_id, sphere_id]
    positions = [cube_position, sphere_position]
    rotations = [cube_rotation, sphere_rotation]
    # Set the color.
    commands.extend([{"$type": "set_color",
                      "id": object_id,
                      "color": {"r": 1, "g": 1, "b": 1, "a": 1}} for object_id in object_ids])
    # Request output data.
    commands.extend([{"$type": "send_albedo_colors"},
                     {"$type": "send_bounds"},
                     {"$type": "send_categories"},
                     {"$type": "send_euler_angles"},
                     {"$type": "send_local_transforms"},
                     {"$type": "send_meshes"},
                     {"$type": "send_segmentation_colors"},
                     {"$type": "send_volumes"},
                     {"$type": "send_transforms"}])
    resp = controller.communicate(commands)
    albedo_colors = AlbedoColors(get_output_data(resp, "acol"))
    assert_num(albedo_colors)
    # Both objects are in the output data and have the correct color.
    for i in range(albedo_colors.get_num()):
        assert albedo_colors.get_id(i) in object_ids
        assert np.sum(albedo_colors.get_color(i).astype(int)) == 255 * 4
    # Test for expected bounds.
    bounds = Bounds(get_output_data(resp, "boun"))
    assert_num(bounds)
    extents = np.zeros(shape=(2, 3))
    for index, object_id in zip([0, 1], object_ids):
        assert bounds.get_id(index) == object_id
        be = TDWUtils.get_bounds_extents(bounds, index)
        assert_arr(be, np.ones(shape=3))
        extents[index] = be
    # Test for expected categories.
    categories = Categories(get_output_data(resp, "cate"))
    assert categories.get_num_categories() == 1
    assert categories.get_category_name(0) == "flex_primitive"
    # Test Euler angles.
    euler_angles = EulerAngles(get_output_data(resp, "eule"))
    assert_num(euler_angles)
    for index, object_id, rotation in zip([0, 1], object_ids, rotations):
        assert euler_angles.get_id(index) == object_id
        assert_arr(euler_angles.get_rotation(index), TDWUtils.vector3_to_array(rotation))
    # Test local transforms.
    local_transforms = LocalTransforms(get_output_data(resp, "ltra"))
    assert_transforms(local_transforms, object_ids, positions, rotations)
    for i, rotation in zip(range(local_transforms.get_num()), rotations):
        assert_arr(local_transforms.get_euler_angles(i), TDWUtils.vector3_to_array(rotation))
    # Test transforms.
    assert_transforms(Transforms(get_output_data(resp, "tran")), object_ids, positions, rotations)
    # Test meshes.
    meshes = Meshes(get_output_data(resp, "mesh"))
    assert_num(meshes)
    for index, object_id, num_vertices, num_triangles in zip([0, 1], object_ids, [96, 205], [108, 320]):
        assert meshes.get_object_id(index) == object_id
        assert len(meshes.get_vertices(index)) == num_vertices
        assert len(meshes.get_triangles(index)) == num_triangles
    # Test segmentation colors.
    segmentation_colors = SegmentationColors(get_output_data(resp, "segm"))
    assert_num(segmentation_colors)
    for i, name in zip(range(segmentation_colors.get_num()), ["cube", "sphere"]):
        assert segmentation_colors.get_object_id(i) in object_ids
        assert segmentation_colors.get_object_name(i) == name
        assert segmentation_colors.get_object_category(i) == "flex_primitive"
    volumes = Volumes(get_output_data(resp, "volu"))
    assert_num(volumes)
    for i in range(volumes.get_num()):
        assert volumes.get_object_id(i) in object_ids
        # Get the expected volume from the bounds extents. (This won't work with more complex geometries!)
        assert_float(volumes.get_volume(i), float(extents[i][0] * extents[i][1] * extents[i][2]))
    # Test the substructure of each model.
    for object_id, name in zip(object_ids, ["cube", "sphere"]):
        resp = controller.communicate({"$type": "send_substructure",
                                       "id": object_id})
        substructure = Substructure(get_output_data(resp, "subs"))
        assert substructure.get_num_sub_objects() == 1
        assert substructure.get_sub_object_name(0) == name
        assert substructure.get_num_sub_object_materials(0) == 1
        assert substructure.get_sub_object_material(0, 0) == "None (Instance)"
    # Enable physics and apply forces.
    resp = controller.communicate([{"$type": "simulate_physics",
                                    "value": True},
                                   {"$type": "apply_force_to_object",
                                    "id": cube_id,
                                    "force": {"x": 12, "y": 1, "z": 0.5}},
                                   {"$type": "send_static_rigidbodies"},
                                   {"$type": "send_rigidbodies"}])
    # Test rigidbodies.
    rigidbodies = Rigidbodies(get_output_data(resp, "rigi"))
    for i in range(rigidbodies.get_num()):
        assert rigidbodies.get_id(i) in object_ids
        assert not rigidbodies.get_sleeping(i)
    assert np.linalg.norm(rigidbodies.get_velocity(0)) > 3.75
    assert np.linalg.norm(rigidbodies.get_angular_velocity(0)) < 0.05
    assert np.linalg.norm(rigidbodies.get_velocity(1)) < 1
    assert np.linalg.norm(rigidbodies.get_angular_velocity(1)) < 0.1
    # Test static rigidbodies.
    static_rigidbodies = StaticRigidbodies(get_output_data(resp, "srig"))
    assert_num(static_rigidbodies)
    for i in range(static_rigidbodies.get_num()):
        assert static_rigidbodies.get_id(i) in object_ids
        assert not static_rigidbodies.get_kinematic(i)
        assert_float(static_rigidbodies.get_static_friction(i), 0.7)
        assert_float(static_rigidbodies.get_dynamic_friction(i), 0.7)
        assert_float(static_rigidbodies.get_bounciness(i), 0.3)


def test_collisions(controller):
    commands = [TDWUtils.create_empty_room(12, 12)]
    object_id_0 = TestController.get_unique_id()
    object_id_1 = TestController.get_unique_id()
    commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                          object_id=object_id_0,
                                                          position={"x": 0, "y": 0.5, "z": 0},
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          static_friction=0.7,
                                                          dynamic_friction=0.7,
                                                          bounciness=0.9,
                                                          mass=3))
    commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                          object_id=object_id_1,
                                                          position={"x": 0, "y": 3, "z": 0},
                                                          library="models_flex.json",
                                                          default_physics_values=False,
                                                          static_friction=0.7,
                                                          dynamic_friction=0.7,
                                                          bounciness=0.9,
                                                          mass=3))
    commands.extend([{"$type": "send_rigidbodies",
                      "frequency": "always"},
                     {"$type": "send_collisions",
                      "enter": True,
                      "stay": False,
                      "exit": True,
                      "collision_types": ["obj", "env"]}])
    resp = controller.communicate(commands)
    sleeping = False
    frame = 0
    while not sleeping and frame < 300:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "coll":
                collision = Collision(resp[i])
                if collision.get_state() == "enter":
                    assert frame == 32

                print(f"collision {collision.get_state()} {collision.get_impulse()} {np.linalg.norm(collision.get_relative_velocity())} {frame}")
            elif r_id == "rigi":
                rigidbodies = Rigidbodies(resp[i])
                sleeping = all([rigidbodies.get_sleeping(index) for index in range(rigidbodies.get_num())])
        resp = controller.communicate([])
        frame += 1
    assert sleeping
    assert frame == 212


def get_output_data(resp: List[bytes], r_id: str) -> bytes:
    for i in range(len(resp) - 1):
        if r_id == OutputData.get_data_type_id(resp[i]):
            return resp[i]
    raise Exception(f"Output data {r_id} not found.")


def assert_num(output_data, expected_num: int = 2) -> None:
    assert output_data.get_num() == expected_num


def assert_float(a: float, b: float, delta: float = 0.0001) -> None:
    assert abs(abs(a) - abs(b)) <= delta


def assert_arr(a: np.ndarray, b: np.ndarray, delta: float = 0.0001) -> None:
    assert a.shape == b.shape
    assert np.linalg.norm(a - b) <= delta


def assert_transforms(data: Union[LocalTransforms, Transforms], object_ids: List[int],
                      positions: List[Dict[str, float]], rotations: List[Dict[str, float]]):
    assert_num(data)
    for index, object_id, position, rotation in zip([0, 1], object_ids, positions, rotations):
        assert data.get_id(index) == object_id
        assert_arr(data.get_position(index), TDWUtils.vector3_to_array(position))
        rot = data.get_rotation(index)
        # Unclear why this needs to be `abs`.
        assert_arr(np.abs(rot), np.abs(QuaternionUtils.euler_angles_to_quaternion(TDWUtils.vector3_to_array(rotation))))
        # Convert the rotation to a directional vector.
        assert_arr(data.get_forward(index), QuaternionUtils.multiply_by_vector(rot, QuaternionUtils.FORWARD))



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
Keyboard
Lights
Magnebot
MagnebotWheels
Mouse
NavMeshPath
ObiParticles
ObjectColliderIntersection
Occlusion
OccupancyMap
OculusTouchButtons
Overlap
Raycast
Replicants
ReplicantSegmentationColors
RobotJointVelocities
SceneRegions
ScreenPosition
StaticCompositeObjects
StaticEmptyObjects
StaticOculusTouch
StaticRobot
TransformMatrices
TriggerCollision
"""