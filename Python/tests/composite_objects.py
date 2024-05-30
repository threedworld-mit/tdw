import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic
from tdw.object_data.composite_object.composite_object_dynamic import CompositeObjectDynamic
from test_controller import TestController
from util import assert_float, assert_arr, controller


"""
Test composite object data and the CompositeObjectManager.

There are tests only for hinges and springs because there aren't any usable models that have motors, lights, etc.
"""


def test_hinge(controller):
    """
    Test a composite object that has a hinge sub-object.

    :param controller: The controller.
    """

    static_object, dynamic_object = init(controller, "b05_db_apps_tech_08_09_composite")
    assert len(static_object.sub_object_ids) == 1
    assert len(static_object.hinges) == 1
    assert len(static_object.springs) == 0
    assert len(static_object.lights) == 0
    assert len(static_object.motors) == 0
    assert len(static_object.non_machines) == 0
    assert len(static_object.prismatic_joints) == 0
    sub_object_id = static_object.sub_object_ids[0]
    hinge = static_object.hinges[sub_object_id]
    assert hinge.sub_object_id == sub_object_id
    assert_arr(hinge.axis, np.zeros(shape=3))
    assert_float(hinge.max_limit, 90)
    assert_float(hinge.min_limit, 0)
    assert hinge.has_limits
    hinge_dynamic(dynamic_object, sub_object_id)


def test_spring(controller):
    """
    Test a composite object that has a spring sub-object.

    :param controller: The controller.
    """

    static_object, dynamic_object = init(controller, "dishwasher_4_composite")
    assert len(static_object.sub_object_ids) == 1
    assert len(static_object.hinges) == 0
    assert len(static_object.springs) == 1
    assert len(static_object.lights) == 0
    assert len(static_object.motors) == 0
    assert len(static_object.non_machines) == 0
    assert len(static_object.prismatic_joints) == 0
    sub_object_id = static_object.sub_object_ids[0]
    spring = static_object.springs[sub_object_id]
    assert spring.sub_object_id == sub_object_id
    assert_float(spring.force, 0)
    assert_float(spring.damper, 0)
    assert_arr(spring.axis, np.zeros(shape=3))
    assert_float(spring.max_limit, 90)
    assert_float(spring.min_limit, 0)
    assert spring.has_limits
    # Test dynamic data.
    hinge_dynamic(dynamic_object, sub_object_id)


def init(controller, model_name: str) -> (CompositeObjectStatic, CompositeObjectDynamic):
    com = CompositeObjectManager()
    controller.add_ons.append(com)
    commands = [TDWUtils.create_empty_room(12, 12)]
    object_id = 100
    commands.extend(TestController.get_add_physics_object(model_name=model_name,
                                                          object_id=object_id))
    controller.communicate(commands)
    # Cache static data.
    controller.communicate([])
    # Test static data.
    assert len(com.static) == 1
    static_object = com.static[object_id]
    assert static_object.object_id == object_id
    # Test dynamic data.
    dynamic_object = com.dynamic[object_id]
    assert dynamic_object.object_id == object_id
    assert len(dynamic_object.hinges) == 1
    return static_object, dynamic_object


def hinge_dynamic(dynamic_object: CompositeObjectDynamic, sub_object_id: int):
    assert len(dynamic_object.hinges) == 1
    hinge = dynamic_object.hinges[sub_object_id]
    assert_float(hinge.angle, 0)
    assert_float(hinge.velocity, 0)
    assert len(dynamic_object.lights) == 0
