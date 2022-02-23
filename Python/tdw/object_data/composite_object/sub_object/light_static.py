from tdw.output_data import StaticCompositeObjects
from tdw.object_data.composite_object.sub_object.sub_object_static import SubObjectStatic


class LightStatic(SubObjectStatic):
    """
    Static data for a light sub-object of a composite object.
    """

    def _get_sub_object_id(self, static_composite_objects: StaticCompositeObjects, object_index: int,
                           sub_object_index: int) -> int:
        return static_composite_objects.get_light_id(object_index, sub_object_index)
