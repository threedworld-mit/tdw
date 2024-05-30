from typing import Dict
from tdw.add_ons.container_manager import ContainerManager
from tdw.tdw_utils import TDWUtils
from tdw.container_data.container_tag import ContainerTag
from test_controller import TestController
from util import controller

"""
Test containment output data for various combinations of container shapes and tags.

Some shape-tag combinations aren't tested because there aren't any models with that combination.

Each container model has exactly one shape. Each test assumes that the container contains the containee.
"""


def test_box_inside(controller):
    containment(controller,
                "basket_18inx18inx12iin_bamboo",
                "cork_plastic",
                {"x": 0, "y": 0.1, "z": 0},
                ContainerTag.inside)


def test_cylinder_inside(controller):
    containment(controller,
                "measuring_pan",
                "b05_cylinder001",
                {"x": 0, "y": 0.06, "z": 0},
                ContainerTag.inside)


def test_sphere_inside(controller):
    containment(controller,
                "vase_05",
                "cork_plastic",
                {"x": 0, "y": 0.1, "z": 0},
                ContainerTag.inside)


def test_box_on(controller):
    containment(controller,
                "small_table_green_marble",
                "b05_cylinder001",
                {"x": 0, "y": 0.89, "z": 0},
                ContainerTag.on)


def test_cylinder_on(controller):
    containment(controller,
                "tolix_bar_stool",
                "b05_cylinder001",
                {"x": 0, "y": 0.62, "z": 0},
                ContainerTag.on)


def test_box_enclosed(controller):
    containment(controller,
                "sink_cabinet_unit_wood_beech_honey_porcelain_composite",
                "b05_cylinder001",
                {"x": 0, "y": 0.5, "z": 0},
                ContainerTag.enclosed)


def containment(controller, model_name_0: str, model_name_1: str, position_1: Dict[str, float], tag: ContainerTag) -> None:
    object_id_0 = 100
    object_id_1 = 101
    container_manager = ContainerManager()
    controller.add_ons.append(container_manager)
    commands = [TDWUtils.create_empty_room(12, 12)]
    commands.extend(TestController.get_add_physics_object(model_name=model_name_0,
                                                          object_id=object_id_0,
                                                          kinematic=True))
    commands.extend(TestController.get_add_physics_object(model_name=model_name_1,
                                                          object_id=object_id_1,
                                                          position=position_1))
    controller.communicate(commands)
    controller.communicate([])
    # There is a containment event.
    assert len(container_manager.container_shapes) == 1
    shape_id = list(container_manager.container_shapes.keys())[0]
    assert container_manager.container_shapes[shape_id] == object_id_0
    assert len(container_manager.tags) == 1
    assert container_manager.tags[shape_id] == tag
    assert len(container_manager.events) == 1
    event = container_manager.events[shape_id]
    assert event.tag == tag
    assert event.container_id == shape_id
    assert len(event.object_ids) == 1
    assert object_id_1 in event.object_ids
