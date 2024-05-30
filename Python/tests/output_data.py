from typing import List, Union, Dict, Type
from pathlib import Path
import pytest
import numpy as np
from tdw.output_data import (OutputData, AlbedoColors, AvatarKinematic, AvatarSimpleBody, AvatarSegmentationColor,
                             AvatarTransformMatrices, Bounds, CameraMatrices, Categories, Collision,
                             EnvironmentCollision, EulerAngles, FieldOfView, IdPassSegmentationColors, Images,
                             ImageSensors, LocalTransforms, Meshes, Occlusion, OccupancyMap, QuitSignal, Raycast,
                             Rigidbodies, ScreenPosition, SegmentationColors, StaticRigidbodies, Substructure, Volumes,
                             Transforms)
from tdw.tdw_utils import TDWUtils
from tdw.quaternion_utils import QuaternionUtils
from test_controller import TestController


FIELD_OF_VIEW: float = 54.4322


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
    entered_object = False
    exited_object = False
    entered_env_0 = 0
    exited_env_0 = 0
    entered_env_1 = 0
    exited_env_1 = 0
    while not sleeping and frame < 300:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "coll":
                collision = Collision(resp[i])
                state = collision.get_state()
                if state == "enter":
                    assert frame == 32
                    assert np.linalg.norm(collision.get_impulse()) > 17
                    assert np.linalg.norm(collision.get_relative_velocity()) > 6
                    entered_object = True
                elif state == "exit":
                    assert frame == 39
                    assert_float(float(np.linalg.norm(collision.get_impulse())), 0)
                    assert np.linalg.norm(collision.get_relative_velocity()) > 3.5
                    exited_object = True
            elif r_id == "enco":
                collision = EnvironmentCollision(resp[i])
                # Count the collision events per object.
                if collision.get_state() == "enter":
                    if collision.get_object_id() == object_id_0:
                        entered_env_0 += 1
                    else:
                        entered_env_1 += 1
                else:
                    if collision.get_object_id() == object_id_0:
                        exited_env_0 += 1
                    else:
                        exited_env_1 += 1
            elif r_id == "rigi":
                rigidbodies = Rigidbodies(resp[i])
                sleeping = all([rigidbodies.get_sleeping(index) for index in range(rigidbodies.get_num())])
        resp = controller.communicate([])
        frame += 1
    assert sleeping
    assert frame == 212
    assert entered_object
    assert exited_object
    assert entered_env_0 == 2
    assert entered_env_1 == 4
    assert exited_env_0 == 1
    assert exited_env_1 == 3


def test_raycast(controller):
    commands = [TDWUtils.create_empty_room(12, 12)]
    scale = 0.2
    arr = np.arange(-2, 2, step=scale * 3)
    object_ids = []
    positions = []
    for x in arr:
        for z in arr:
            object_id = TestController.get_unique_id()
            position = {"x": float(x), "y": 0, "z": float(z)}
            commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                                  object_id=object_id,
                                                                  library="models_flex.json",
                                                                  position=position,
                                                                  scale_factor={"x": scale, "y": scale, "z": scale},
                                                                  kinematic=True))
            object_ids.append(object_id)
            positions.append(position)
    # Raycast some, but not all, objects.
    for index in [2, 4, 6]:
        position = positions[index]
        commands.append({"$type": "send_raycast",
                         "id": object_ids[index],
                         "origin": {"x": position["x"], "y": 100, "z": position["z"]},
                         "destination": position})
    # Raycast the scene.
    raycast_scene_id = TestController.get_unique_id()
    d = 3
    commands.append({"$type": "send_raycast",
                     "id": raycast_scene_id,
                     "origin": {"x": d, "y": 100, "z": d},
                     "destination": {"x": d, "y": 0, "z": d}})
    # Raycast the void.
    raycast_void_id = TestController.get_unique_id()
    d = 100
    commands.append({"$type": "send_raycast",
                     "id": raycast_void_id,
                     "origin": {"x": d, "y": 100, "z": d},
                     "destination": {"x": d, "y": 0, "z": d}})
    resp = controller.communicate(commands)
    for i in range(len(resp) - 1):
        # There shouldn't be any other output data.
        assert OutputData.get_data_type_id(resp[i]) == "rayc"
        raycast = Raycast(resp[i])
        raycast_id = raycast.get_raycast_id()
        # This raycast hit an object.
        if raycast_id in object_ids:
            assert raycast.get_hit()
            assert raycast.get_hit_object()
            assert raycast.get_object_id() == raycast_id
            assert raycast.get_point()[1] >= scale
            assert_arr(np.array(raycast.get_normal()), np.array([0, 1, 0]))
        # This raycast hit the floor.
        elif raycast_id == raycast_scene_id:
            assert raycast.get_hit()
            assert not raycast.get_hit_object()
            assert_arr(np.array(raycast.get_normal()), np.array([0, 1, 0]))
        elif raycast_id == raycast_void_id:
            assert not raycast.get_hit()
            assert not raycast.get_hit_object()
        else:
            raise Exception(f"Unexpected raycast ID: {raycast_id}")
    # Test the occupancy map.
    resp = controller.communicate({"$type": "send_occupancy_map"})
    assert len(resp) == 2
    assert OutputData.get_data_type_id(resp[0]) == "occu"
    occupancy_map = OccupancyMap(resp[0])
    assert tuple(occupancy_map.get_shape()) == (23, 23)
    occupancy = occupancy_map.get_map()
    for row in range(7, 9):
        for col in range(7, 14):
            assert occupancy[row][col] == 1
    assert occupancy[10][10] == 3
    for row in range(11, 14):
        for col in range(7, 14):
            assert occupancy[row][col] == 1


def get_output_data(resp: List[bytes], r_id: str) -> bytes:
    for i in range(len(resp) - 1):
        if r_id == OutputData.get_data_type_id(resp[i]):
            return resp[i]
    raise Exception(f"Output data {r_id} not found.")


def assert_num(output_data, expected_num: int = 2) -> None:
    assert output_data.get_num() == expected_num


def assert_float(a: float, b: float, delta: float = 0.0001) -> None:
    c = abs(abs(a) - abs(b))
    if c > delta:
        print(f"{a}, {b}, {c}")
    assert c <= delta


def assert_arr(a: np.ndarray, b: np.ndarray, delta: float = 0.0001) -> None:
    assert a.shape == b.shape
    c = np.linalg.norm(a - b)
    if c > delta:
        print(f"{a}, {b}, {c}")
    assert c <= delta


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


def test_avatars(controller):
    # Test each avatar.
    simple_body = avatar(controller, "A_Simple_Body", AvatarSimpleBody, "avsb", 28)
    assert isinstance(simple_body, AvatarSimpleBody)
    assert simple_body.get_visible_body() == "Capsule"
    # Test the avatar's segmentation color.
    resp = controller.communicate([{"$type": "send_avatar_segmentation_colors"}])
    avatar_segmentation_color = AvatarSegmentationColor(get_output_data(resp, "avsc"))
    assert avatar_segmentation_color.get_id() == "a"
    # Test the other avatars.
    avatar(controller, "A_Img_Caps_Kinematic", AvatarKinematic, "avki", 32)
    avatar(controller, "A_First_Person", AvatarKinematic, "avki", 32)


def avatar(controller, avatar_type: str, output_data_type: Type[AvatarKinematic], avatar_data_id: str,
           occlusion_value: int) -> AvatarKinematic:
    png = False
    # Create a scene. Add an object. Add an avatar. Look at the object. Send output data.
    avatar_position = {"x": 3, "y": 2, "z": 0}
    pass_masks = ["_img", "_id", "_category", "_mask", "_depth", "_depth_simple", "_normals", "_flow", "_albedo"]
    screen_position_v3 = {"x": 0.5, "y": 1, "z": 1}
    commands = [{"$type": "load_scene",
                 "scene_name": "ProcGenScene"},
                TDWUtils.create_empty_room(12, 12),
                {"$type": "simulate_physics",
                 "value": False},
                TestController.get_add_object(model_name="cube",
                                              object_id=0,
                                              library="models_flex.json"),
                {"$type": "create_avatar", "type": avatar_type},
                {"$type": "teleport_avatar_to", "position": avatar_position},
                {"$type": "look_at",
                 "object_id": 0,
                 "use_centroid": True},
                {"$type": "send_avatars"},
                {"$type": "send_image_sensors"},
                {"$type": "send_avatar_transform_matrices"},
                {"$type": "send_camera_matrices"},
                {"$type": "send_field_of_view"},
                {"$type": "set_post_process",
                 "value": False},
                {"$type": "set_render_quality",
                 "render_quality": 0},
                {"$type": "set_img_pass_encoding",
                 "value": png},
                {"$type": "set_pass_masks",
                 "pass_masks": pass_masks},
                {"$type": "send_images"},
                {"$type": "send_occlusion"},
                {"$type": "send_segmentation_colors"},
                {"$type": "send_id_pass_segmentation_colors"},
                {"$type": "send_screen_positions",
                 "position_ids": [0],
                 "positions": [screen_position_v3]}]
    resp = controller.communicate(commands)
    # Test avatar data.
    a: output_data_type = output_data_type(get_output_data(resp, avatar_data_id))
    assert a.get_avatar_id() == "a"
    # Compare the transforms.
    assert_arr(np.array(a.get_position()), TDWUtils.vector3_to_array(avatar_position))
    assert_arr(np.array(a.get_rotation()), QuaternionUtils.IDENTITY)
    assert_arr(np.array(a.get_forward()), QuaternionUtils.FORWARD)
    # Test transform matrices.
    avatar_transform_matrices = AvatarTransformMatrices(get_output_data(resp, "atrm"))
    assert avatar_transform_matrices.get_num() == 1
    assert avatar_transform_matrices.get_id(0) == "a"
    assert_arr(avatar_transform_matrices.get_avatar_matrix(0), np.load("transform_matrices/avatar.npy"))
    # Test camera matrices.
    camera_matrices = CameraMatrices(get_output_data(resp, "cama"))
    assert camera_matrices.get_avatar_id() == "a"
    assert camera_matrices.get_sensor_name() == "SensorContainer"
    # Compare the matrices to a canonical matrices.
    assert_arr(camera_matrices.get_projection_matrix(), np.load("camera_matrices/projection_matrix.npy"))
    assert_arr(camera_matrices.get_camera_matrix(), np.load(f"camera_matrices/{avatar_type.lower()}.npy"))
    # Test field of view.
    field_of_view = FieldOfView(get_output_data(resp, "fofv"))
    assert field_of_view.get_avatar_id() == "a"
    assert_float(field_of_view.get_fov(), FIELD_OF_VIEW)
    assert field_of_view.get_sensor_name() == "SensorContainer"
    assert_float(field_of_view.get_focal_length(), 35)
    # Test images.
    images = Images(get_output_data(resp, "imag"))
    assert images.get_avatar_id() == "a"
    assert images.get_sensor_name() == "SensorContainer"
    assert images.get_width() == 256
    assert images.get_height() == 256
    assert images.get_num_passes() == len(pass_masks)
    image_directory = Path("image_passes").joinpath(avatar_type)
    if not image_directory.exists():
        image_directory.mkdir(parents=True)
    # Compare each image to a canonical image.
    for i in range(images.get_num_passes()):
        assert images.get_extension(i) == ("png" if i > 0 else "jpg")
        assert images.get_pass_mask(i) in pass_masks
        assert_arr(images.get_image(i), np.load(str(image_directory.joinpath(f"{images.get_pass_mask(i)}.npy"))))
    # Test image sensor data.
    image_sensors = ImageSensors(get_output_data(resp, "imse"))
    assert image_sensors.get_avatar_id() == "a"
    assert image_sensors.get_num_sensors() == 1
    assert_float(image_sensors.get_sensor_field_of_view(0), FIELD_OF_VIEW)
    assert image_sensors.get_sensor_on(0)
    assert image_sensors.get_sensor_name(0) == "SensorContainer"
    # We're not going to test rotation because it varies between avatars.
    # Test occlusion.
    occlusion = Occlusion(get_output_data(resp, "occl"))
    assert occlusion.get_avatar_id() == "a"
    assert occlusion.get_occluded() == occlusion_value
    assert occlusion.get_unoccluded() == occlusion_value
    # Test screen position.
    screen_position = ScreenPosition(get_output_data(resp, "scre"))
    assert screen_position.get_id() == 0
    assert screen_position.get_avatar_id() == "a"
    assert screen_position.get_sensor_name() == "SensorContainer"
    assert_arr(np.array(screen_position.get_world()), TDWUtils.vector3_to_array(screen_position_v3))
    assert_arr(np.array(screen_position.get_screen()).astype(int), np.array([213, 140, 3]), delta=12)
    # Test segmentation colors.
    segmentation_color = tuple(SegmentationColors(get_output_data(resp, "segm")).get_object_color(0))
    id_pass_segmentation_colors = IdPassSegmentationColors(get_output_data(resp, "ipsc"))
    assert id_pass_segmentation_colors.get_avatar_id() == "a"
    assert id_pass_segmentation_colors.get_num_segmentation_colors() == 1
    assert tuple(id_pass_segmentation_colors.get_segmentation_color(0)) == segmentation_color
    return a


"""
AudioSourceDone
AudioSources
Containment
Drones
DynamicCompositeObjects
DynamicEmptyObjects
DynamicRobots
EnvironmentColliderIntersections
Framerate
IsOnNavMesh
Lights
Magnebot
MagnebotWheels
NavMeshPath
ObiParticles
ObjectColliderIntersection
Overlap
Replicants
ReplicantSegmentationColors
SceneRegions
StaticCompositeObjects
StaticEmptyObjects
StaticOculusTouch
StaticRobot
TransformMatrices
TriggerCollision
"""

"""
https://threedw.slack.com/archives/D0456ALLE3S/p1705091578099959
https://threedw.slack.com/archives/D0456ALLE3S/p1705091613415289
https://threedw.slack.com/archives/D0456ALLE3S/p1705091631268829
"""