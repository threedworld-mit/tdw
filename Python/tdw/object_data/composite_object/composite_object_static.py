from typing import Dict, List
from tdw.output_data import StaticCompositeObjects
from tdw.object_data.composite_object.sub_object.non_machine_static import NonMachineStatic
from tdw.object_data.composite_object.sub_object.light_static import LightStatic
from tdw.object_data.composite_object.sub_object.hinge_static import HingeStatic
from tdw.object_data.composite_object.sub_object.spring_static import SpringStatic
from tdw.object_data.composite_object.sub_object.motor_static import MotorStatic
from tdw.object_data.composite_object.sub_object.prismatic_joint_static import PrismaticJointStatic


class CompositeObjectStatic:
    """
    Static data for a composite object and its sub-objects.
    """

    def __init__(self, static_composite_objects: StaticCompositeObjects, object_index: int):
        """
        :param static_composite_objects: The `StaticCompositeObjects` output data.
        :param object_index: The index in `static_composite_objects.get_object_id()`.
        """

        """:field
        The ID of the root object.
        """
        self.object_id: int = static_composite_objects.get_object_id(object_index)
        """:field
        [`NonMachineStatic`](sub_object/non_machine_static.md) sub-objects such as puzzle pieces. Key = The sub-object ID.
        """
        self.non_machines: Dict[int, NonMachineStatic] = dict()
        for i in range(static_composite_objects.get_num_non_machines(object_index)):
            sub_object = NonMachineStatic(static_composite_objects, object_index, i)
            self.non_machines[sub_object.sub_object_id] = sub_object
        """:field
        [`LightStatic`](sub_object/light_static.md) sub-objects such as lamp lightbulbs. Key = The sub-object ID.
        """
        self.lights: Dict[int, LightStatic] = dict()
        for i in range(static_composite_objects.get_num_lights(object_index)):
            sub_object = LightStatic(static_composite_objects, object_index, i)
            self.lights[sub_object.sub_object_id] = sub_object
        """:field
        [`HingeStatic`](sub_object/hinge_static.md) sub-objects such as doors. Key = The sub-object ID.
        """
        self.hinges: Dict[int, HingeStatic] = dict()
        for i in range(static_composite_objects.get_num_hinges(object_index)):
            sub_object = HingeStatic(static_composite_objects, object_index, i)
            self.hinges[sub_object.sub_object_id] = sub_object
        """:field
        [`SpringStatic`](sub_object/spring_static.md) sub-objects such as an oven door (which has a damper value). Key = The sub-object ID.
        """
        self.springs: Dict[int, SpringStatic] = dict()
        for i in range(static_composite_objects.get_num_springs(object_index)):
            sub_object = SpringStatic(static_composite_objects, object_index, i)
            self.springs[sub_object.sub_object_id] = sub_object
        """:field
        [`MotorStatic`](sub_object/motor_static.md) sub-objects such as a ceiling fan. Key = The sub-object ID.
        """
        self.motors: Dict[int, MotorStatic] = dict()
        for i in range(static_composite_objects.get_num_motors(object_index)):
            sub_object = MotorStatic(static_composite_objects, object_index, i)
            self.motors[sub_object.sub_object_id] = sub_object
        """:field
        [`PrismaticJointStatic`](sub_object/prismatic_joint_static.md) sub-objects such as a desk drawer. Key = The sub-object ID.
        """
        self.prismatic_joints: Dict[int, PrismaticJointStatic] = dict()
        for i in range(static_composite_objects.get_num_prismatic_joints(object_index)):
            sub_object = PrismaticJointStatic(static_composite_objects, object_index, i)
            self.prismatic_joints[sub_object.sub_object_id] = sub_object
        """:field
        A flat list of all sub-object IDs.
        """
        self.sub_object_ids: List[int] = list()
        self.sub_object_ids.extend(self.non_machines.keys())
        self.sub_object_ids.extend(self.lights.keys())
        self.sub_object_ids.extend(self.hinges.keys())
        self.sub_object_ids.extend(self.springs.keys())
        self.sub_object_ids.extend(self.motors.keys())
        self.sub_object_ids.extend(self.prismatic_joints.keys())
