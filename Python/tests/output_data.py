from typing import List, Union, Dict, Type
from pathlib import Path
import pytest
import numpy as np
from tdw.output_data import (OutputData, AlbedoColors, AvatarKinematic, AvatarSimpleBody, AvatarSegmentationColor,
                             AvatarTransformMatrices, Bounds, CameraMatrices, Categories, Collision,
                             DynamicEmptyObjects, EnvironmentColliderIntersection, EnvironmentCollision, EulerAngles,
                             FieldOfView, IdPassSegmentationColors, Images, IsOnNavMesh, ImageSensors, Lights,
                             LocalTransforms, Meshes, NavMeshPath, ObjectColliderIntersection, Occlusion, OccupancyMap,
                             Overlap, Raycast, Rigidbodies, SceneRegions, ScreenPosition, SegmentationColors,
                             StaticEmptyObjects, StaticRigidbodies, Substructure, Volumes, Transforms)
from tdw.tdw_utils import TDWUtils
from tdw.quaternion_utils import QuaternionUtils
from test_controller import TestController
from util import get_output_data, assert_float, assert_arr, controller


"""
Unit tests for most, but not all, output data types.

Excluded output data types include:
    - Types used by agents (e.g. StaticRobot)
    - Types that require user input and/or special hardware (e.g. VRRig)
    - Types require audio (e.g. AudioSources)
    - Types that we can assume always work (e.g. Version)
    - Types that should be tested via an AddOn (e.g. composite object data)
"""


FIELD_OF_VIEW: float = 54.4322


def test_object_output_data(controller):
    """
    Test per-object data for two objects in the scene.
    """

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
    """
    Add two objects to the scene and test for expected collision data.
    """

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
    """
    Test raycast data.
    """

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


def assert_num(output_data, expected_num: int = 2) -> None:
    """
    Assert that the output data's `get_num()` method returns `expected_num`
    """

    assert output_data.get_num() == expected_num


def assert_transforms(data: Union[LocalTransforms, Transforms], object_ids: List[int],
                      positions: List[Dict[str, float]], rotations: List[Dict[str, float]]):
    """
    Assert that `data` is transform data and that it matches expected IDs, positions, and rotations.
    """

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
    """
    Test each type of avatar, including transform data and image capture.
    """

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
    """
    Per-avatar tests.
    """

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


def test_scene(controller):
    """
    Test scene and NavMesh output data.
    """

    is_on_nav_mesh_position = {"x": 1, "y": 0, "z": -0.76}
    nav_mesh_path_0 = {"x": 1, "y": 0, "z": -1}
    nav_mesh_path_1 = {"x": -1.5, "y": 0, "z": 1.5}
    resp = controller.communicate([TestController.get_add_scene("tdw_room"),
                                   {"$type": "send_lights"},
                                   {"$type": "send_scene_regions"},
                                   {"$type": "bake_nav_mesh"},
                                   {"$type": "send_is_on_nav_mesh",
                                    "position": is_on_nav_mesh_position},
                                   {"$type": "send_nav_mesh_path",
                                    "origin": nav_mesh_path_0,
                                    "destination": nav_mesh_path_1}])
    # Test lights.
    lights = Lights(get_output_data(resp, "ligh"))
    assert lights.get_num_directional_lights() == 1
    assert_float(lights.get_directional_light_intensity(0), 1.25)
    assert_arr(np.array(lights.get_directional_light_color(0)), np.array([255, 244, 214]))
    assert lights.get_num_point_lights() == 1
    assert_float(lights.get_point_light_intensity(0), 1.25)
    assert_arr(np.array(lights.get_point_light_color(0)), np.array([255, 255, 255]))
    assert_float(lights.get_point_light_range(0), 10)
    # Test scene regions.
    scene_regions = SceneRegions(get_output_data(resp, "sreg"))
    assert scene_regions.get_num() == 1
    assert scene_regions.get_id(0) == 0
    assert_arr(np.array(scene_regions.get_center(0)), np.array([-0.2965, 0, 0.3843]))
    assert_arr(np.array(scene_regions.get_bounds(0)), np.array([8.2549, 3.3887, 8.3651]))
    # Test nav mesh.
    is_on_nav_mesh = IsOnNavMesh(get_output_data(resp, "isnm"))
    assert is_on_nav_mesh.get_id() == 0
    assert is_on_nav_mesh.get_is_on()
    assert_arr(np.array(is_on_nav_mesh.get_position()), TDWUtils.vector3_to_array(is_on_nav_mesh_position), delta=0.1)
    # Test nav mesh path.
    nav_mesh_path = NavMeshPath(get_output_data(resp, "path"))
    assert nav_mesh_path.get_state() == "complete"
    assert nav_mesh_path.get_id() == 0
    assert_arr(nav_mesh_path.get_path(),
               np.array([TDWUtils.vector3_to_array(nav_mesh_path_0),
                         TDWUtils.vector3_to_array(nav_mesh_path_1)]),
               delta=0.1)


def test_empty_objects(controller):
    """
    Test affordance points (empy objects).
    """

    object_id = 100
    commands = [TDWUtils.create_empty_room(12, 12)]
    commands.extend(TestController.get_add_physics_object(model_name="basket_18inx18inx12iin_bamboo",
                                                          object_id=object_id,
                                                          kinematic=True))
    commands.extend([{"$type": "send_static_empty_objects"},
                     {"$type": "send_dynamic_empty_objects"}])
    resp = controller.communicate(commands)
    # Test static data.
    static_empty_objects = StaticEmptyObjects(get_output_data(resp, "stem"))
    assert static_empty_objects.get_num() == 4
    for i in range(static_empty_objects.get_num()):
        assert static_empty_objects.get_object_id(i) == object_id
    dynamic_empty_objects = DynamicEmptyObjects(get_output_data(resp, "dyem"))
    # Test dynamic data.
    assert dynamic_empty_objects.get_num() == 4
    assert_dynamic_empty_object(dynamic_empty_objects, 0, x_value=True, x_positive=False)
    assert_dynamic_empty_object(dynamic_empty_objects, 1, x_value=True)
    assert_dynamic_empty_object(dynamic_empty_objects, 2, z_value=True)
    assert_dynamic_empty_object(dynamic_empty_objects, 3, z_value=True, z_positive=False)


def assert_dynamic_empty_object(dynamic_empty_objects: DynamicEmptyObjects, index: int,
                                x_value: bool = False, x_positive: bool = True,
                                z_value: bool = False, z_positive: bool = True) -> None:
    """
    Test dynamic empty object positions.

    The model is a basket with evenly-spaced empty objects.

    :param dynamic_empty_objects: The deserialized output data.
    :param index: The index of the empty object.
    :param x_value: If True, x = 0.2285. If False, x = 0.
    :param x_positive: Whether x is positive or negative.
    :param z_value: If True, z = 0.2285. If False, z = 0.
    :param z_positive: Whether z is positive or negative.
    """

    x = 0.2285 if x_value else 0
    if not x_positive:
        x = -x
    z = 0.2285 if z_value else 0
    if not z_positive:
        z = -z
    assert_arr(dynamic_empty_objects.get_position(index), np.array([x, 0.305, z]))


def test_collider_intersections(controller):
    """
    Test collider intersection data between an object intersecting with the floor and an object intersecting with an object.
    """

    object_id_0 = 100
    object_id_1 = 101
    resp = controller.communicate([TestController.get_add_scene("mm_kitchen_1a"),
                                   TestController.get_add_object(model_name="cube",
                                                                 object_id=object_id_0,
                                                                 library="models_flex.json",
                                                                 position={"x": 0, "y": -0.1, "z": 0}),
                                   TestController.get_add_object(model_name="cube",
                                                                 object_id=object_id_1,
                                                                 library="models_flex.json",
                                                                 position={"x": 0, "y": 0.2, "z": 0}),
                                   {"$type": "send_collider_intersections",
                                    "obj_intersection_ids": [[object_id_0, object_id_1]],
                                    "env_intersection_ids": [object_id_0, object_id_1]}])
    assert len(resp) == 3
    # Environment intersection.
    env = EnvironmentColliderIntersection(get_output_data(resp, "enci"))
    assert env.get_object_id() == object_id_0
    assert_float(env.get_distance(), 0.02, delta=0.001)
    # Objects intersection.
    obj = ObjectColliderIntersection(get_output_data(resp, "obci"))
    assert obj.get_object_id_a() == object_id_0
    assert obj.get_object_id_b() == object_id_1
    assert_float(obj.get_distance(), 0.5, delta=0.001)


def test_overlap(controller):
    """
    Test each overlap shape.
    """

    object_id = 100
    commands = [TDWUtils.create_empty_room(12, 12)]
    commands.extend(TestController.get_add_physics_object(model_name="cube",
                                                          object_id=object_id,
                                                          library="models_flex.json",
                                                          kinematic=True))
    box_id = 0
    capsule_id = 1
    sphere_id = 2
    commands.extend([{"$type": "send_overlap_box",
                      "id": box_id,
                      "position": {"x": 0, "y": 0.5, "z": 0},
                      "rotation": TDWUtils.array_to_vector4(
                          QuaternionUtils.euler_angles_to_quaternion(np.array([25, 35, 5]))),
                      "half_extents": {"x": 0.25, "y": 0.5, "z": 0.1}},
                     {"$type": "send_overlap_capsule",
                      "id": capsule_id,
                      "position": {"x": 4, "y": 0.5, "z": 0},
                      "end": {"x": 5, "y": 1.5, "z": -0.1},
                      "radius": 0.5},
                     {"$type": "send_overlap_sphere",
                      "id": sphere_id,
                      "radius": 2,
                      "position": {"x": 1, "y": 0.5, "z": -0.75}}])
    resp = controller.communicate(commands)
    assert len(resp) == 4
    overlap_ids = [box_id, capsule_id, sphere_id]
    for i in range(len(resp) - 1):
        assert OutputData.get_data_type_id(resp[i]) == "over"
        overlap = Overlap(resp[i])
        overlap_id = overlap.get_id()
        assert overlap_id in overlap_ids
        object_ids = overlap.get_object_ids()
        assert overlap.get_env()
        if overlap_id == box_id or overlap_id == sphere_id:
            assert len(object_ids) == 1
            assert object_ids[0] == object_id
            assert not overlap.get_walls()
        elif overlap_id == capsule_id:
            assert len(object_ids) == 0
            assert overlap.get_walls()
        else:
            raise Exception(f"Invalid overlap ID: {overlap_id}")
