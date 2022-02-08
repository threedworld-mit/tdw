from typing import Dict
from tdw.output_data import DynamicCompositeObjects
from tdw.object_data.composite_object.sub_object.light_dynamic import LightDynamic
from tdw.object_data.composite_object.sub_object.hinge_dynamic import HingeDynamic


class CompositeObjectDynamic:
    """
    Dynamic data for a composite object and its sub-objects.
    
    Note that not all sub-objects will be in this output data because some of them don't have specialized dynamic properties.
    For example, non-machines have dynamic positions, velocities, etc. but these can be found in `Transforms` and `Rigidbodies` data, respectively.
    """

    def __init__(self, dynamic_composite_objects: DynamicCompositeObjects, object_index: int):
        """
        :param dynamic_composite_objects: The `DynamicCompositeObjects` output data.
        :param object_index: The index in `dynamic_composite_objects.get_object_id()`.
        """

        """:field
        The ID of the root object.
        """
        self.object_id = dynamic_composite_objects.get_object_id(object_index)
        """:field
        [`LightDynamic`](sub_object/light_dynamic.md) sub-objects such as lamp lightbulbs. Key = The sub-object ID.
        """
        self.lights: Dict[int, LightDynamic] = dict()
        for i in range(dynamic_composite_objects.get_num_lights(object_index)):
            light = LightDynamic(dynamic_composite_objects=dynamic_composite_objects, object_index=object_index,
                                 sub_object_index=i)
            self.lights[light.sub_object_id] = light
        """:field
        [`HingeDynamic`](sub_object/hinge_dynamic.md) sub-objects. *This includes the root object's hinges, springs, and motors.* Key = The sub-object ID.
        """
        self.hinges: Dict[int, HingeDynamic] = dict()
        for i in range(dynamic_composite_objects.get_num_hinges(object_index)):
            hinge = HingeDynamic(dynamic_composite_objects=dynamic_composite_objects, object_index=object_index,
                                 sub_object_index=i)
            self.hinges[hinge.sub_object_id] = hinge
