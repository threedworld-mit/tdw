from pkg_resources import resource_filename
from pathlib import Path
from json import loads
from typing import Dict, Union
from tdw.obi_data.material_combine_mode import MaterialCombineMode


class CollisionMaterial:
    """
    Data for an Obi collision material. For more information, [read this](http://obi.virtualmethodstudio.com/manual/6.3/collisionmaterials.html).
    """

    def __init__(self, dynamic_friction: float, static_friction: float, stickiness: float, stick_distance: float,
                 friction_combine: Union[int, MaterialCombineMode], stickiness_combine: Union[int, MaterialCombineMode]):
        """
        :param dynamic_friction: Percentage of relative tangential velocity removed in a collision, once the static friction threshold has been surpassed and the particle is moving relative to the surface. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        :param static_friction: Percentage of relative tangential velocity removed in a collision. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        :param stickiness: Amount of inward normal force applied between objects in a collision. 0 means no force will be applied, 1 will keep objects from separating once they collide.
        :param stick_distance: Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated.
        :param friction_combine: A [`MaterialCombineMode`](material_combine_mode.md) value describing how friction values are combined.
        :param stickiness_combine: A [`MaterialCombineMode`](material_combine_mode.md) value describing how stickiness values are combined.
        """

        """:field
        Percentage of relative tangential velocity removed in a collision, once the static friction threshold has been surpassed and the particle is moving relative to the surface. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        """
        self.dynamic_friction: float = dynamic_friction
        """:field
        Percentage of relative tangential velocity removed in a collision. 0 means things will slide as if made of ice, 1 will result in total loss of tangential velocity.
        """
        self.static_friction: float = static_friction
        """:field
        Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated.
        """
        self.stickiness: float = stickiness
        """:field
        Maximum distance between objects at which sticky forces are applied. Since contacts will be generated between bodies within the stick distance, it should be kept as small as possible to reduce the amount of contacts generated.
        """
        self.stick_distance: float = stick_distance
        """:field
        A [`MaterialCombineMode`](material_combine_mode.md) value describing how friction values are combined.
        """
        self.friction_combine: MaterialCombineMode = friction_combine if isinstance(friction_combine, MaterialCombineMode) else MaterialCombineMode(int(friction_combine))
        """:field
        A [`MaterialCombineMode`](material_combine_mode.md) value describing how stickiness values are combined.
        """
        self.stickiness_combine: MaterialCombineMode = stickiness_combine if isinstance(stickiness_combine, MaterialCombineMode) else MaterialCombineMode(int(stickiness_combine))

    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {k: v for k, v in self.__dict__.items()}
        d["friction_combine"] = d["friction_combine"].name
        d["stickiness_combine"] = d["stickiness_combine"].name
        return d


def __get() -> Dict[str, CollisionMaterial]:
    data = loads(Path(resource_filename(__name__, "data/collision_materials.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = CollisionMaterial(**data[k])
    return materials


COLLISION_MATERIALS: Dict[str, CollisionMaterial] = __get()
DEFAULT_MATERIAL = CollisionMaterial(dynamic_friction=0.3, static_friction=0.3, stickiness=0, stick_distance=0,
                                     friction_combine=MaterialCombineMode.average,
                                     stickiness_combine=MaterialCombineMode.average)
