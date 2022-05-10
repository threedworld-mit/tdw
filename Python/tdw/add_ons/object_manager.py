from typing import Dict, List
import numpy as np
from tdw.output_data import OutputData, Transforms, Rigidbodies, Bounds, SegmentationColors, Categories, \
    StaticRigidbodies
from tdw.add_ons.add_on import AddOn
from tdw.object_data.object_static import ObjectStatic
from tdw.object_data.transform import Transform
from tdw.object_data.rigidbody import Rigidbody
from tdw.object_data.bound import Bound


class _StaticRigidbody:
    """
    Temporary structure for static rigidbody data.
    """

    def __init__(self, mass: float, kinematic: bool, dynamic_friction, static_friction: float, bounciness: float):
        """
        :param mass: The mass of the object.
        :param dynamic_friction: The dynamic friction of the object.
        :param static_friction: The static friction of the object.
        :param bounciness: The bounciness of the object.
        :param kinematic: If True, this object is kinematic, and won't respond to physics.
        """

        """:field
        If True, this object is kinematic, and won't respond to physics. 
        Examples: a painting hung on a wall or built-in furniture like a countertop.
        """
        self.kinematic = kinematic
        """:field
        The mass of the object.
        """
        self.mass = mass
        """:field
        The dynamic friction of the object.
        """
        self.dynamic_friction: float = dynamic_friction
        """:field
        The static friction of the object.
        """
        self.static_friction: float = static_friction
        """:field
        The bounciness of the object.
        """
        self.bounciness: float = bounciness


class ObjectManager(AddOn):
    """
    A simple manager class for objects in the scene. This add-on can cache static object data (name, ID, etc.) and record dynamic data (position, velocity, etc.) per frame.

    ## Usages constraints:

    - This add-on assumes that this is a PhysX simulation, as opposed to a simulation with physics disabled or a Flex simulation.
    - This add-on will record data for *all* objects in the scene. If you only need data for specific objects, you should use low-level TDW commands.
    - By default, this add-on will record [transform data](../object_data/transform.md) but not [rigidbody data](../object_data/rigidbody.md) or [bounds data](../object_data/bound.md). You can set which data the add-on will record in the constructor, but be aware that this can slow down the simulation.

    ## Example usage

    ```python
    import numpy as np
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.librarian import ModelLibrarian
    from tdw.add_ons.object_manager import ObjectManager


    c = Controller()
    c.model_librarian = ModelLibrarian("models_special.json")
    # Create the object manager.
    om = ObjectManager()
    c.add_ons.append(om)
    commands = [TDWUtils.create_empty_room(100, 100)]
    # The starting height of the objects.
    y = 10
    # The radius of the circle of objects.
    r = 7.0
    # Get all points within the circle defined by the radius.
    p0 = np.array((0, 0))
    o_id = 0
    for x in np.arange(-r, r, 1):
        for z in np.arange(-r, r, 1):
            p1 = np.array((x, z))
            dist = np.linalg.norm(p0 - p1)
            if dist < r:
                commands.extend([c.get_add_object("prim_cone",
                                                  object_id=o_id,
                                                  position={"x": x, "y": y, "z": z},
                                                  rotation={"x": 0, "y": 0, "z": 180})])
                o_id += 1
    pass
    c.communicate(commands)
    for i in range(1000):
        for object_id in om.transforms:
            print(object_id, om.transforms[object_id].position)
        c.communicate([])
    c.communicate({"$type": "terminate"})
    ```
    """
    def __init__(self, transforms: bool = True, rigidbodies: bool = False, bounds: bool = False):
        """
        :param transforms: If True, record the [transform data](../object_data/transform.md) of each object in the scene.
        :param rigidbodies: If True, record the [rigidbody data](../object_data/rigidbody.md) of each rigidbody object in the scene.
        :param bounds: If True, record the [bounds data](../object_data/bound.md) of each object in the scene.
        """

        super().__init__()
        self._cached_static_data: bool = False
        self._send_transforms: str = "always" if transforms else "never"
        self._send_rigidbodies: str = "always" if rigidbodies else "never"
        self._send_bounds: str = "always" if bounds else "once"
        """:field
        [The static object data.](../object_data/object_static.md) Key = The ID of the object.
        """
        self.objects_static: Dict[int, ObjectStatic] = dict()
        """:field
        The segmentation color per category as use in the _category image pass. Key = The category. Value = The color as an `[r, g, b]` numpy array.
        """
        self.categories: Dict[str, np.array] = dict()
        """:field
        The [transform data](../object_data/transform.md) for each object on the scene on this frame. Key = The object ID. If `transforms=False` in the constructor, this dictionary will be empty.
        """
        self.transforms: Dict[int, Transform] = dict()
        """:field
        The [rigidbody data](../object_data/rigidbody.md) for each rigidbody object on the scene on this frame. Key = The object ID. If `rigidbodies=False` in the constructor, this dictionary will be empty.
        """
        self.rigidbodies: Dict[int, Rigidbody] = dict()
        """:field
        The [bounds data](../object_data/bound.md) for each object on the scene on this frame. Key = The object ID. If `bounds=False` in the constructor, this dictionary will be empty.
        """
        self.bounds: Dict[int, Bound] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_categories"},
                {"$type": "send_static_rigidbodies"},
                {"$type": "send_rigidbodies",
                 "frequency": self._send_rigidbodies},
                {"$type": "send_bounds",
                 "frequency": self._send_bounds},
                {"$type": "send_transforms",
                 "frequency": self._send_transforms}]

    def on_send(self, resp: List[bytes]) -> None:
        # Cache static data.
        if not self._cached_static_data:
            self._cached_static_data = True
            # Sort the static output data by object ID.
            segmentation_colors: Dict[int, np.array] = dict()
            names: Dict[int, str] = dict()
            static_rigidbodies: Dict[int, _StaticRigidbody] = dict()
            sizes: Dict[int, np.array] = dict()
            categories: Dict[int, str] = dict()
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Get the name and the segmentation color.
                if r_id == "segm":
                    segm = SegmentationColors(resp[i])
                    for j in range(segm.get_num()):
                        object_id = segm.get_object_id(j)
                        segmentation_colors[object_id] = np.array(segm.get_object_color(j))
                        names[object_id] = segm.get_object_name(j).lower()
                        categories[object_id] = segm.get_object_category(j)
                elif r_id == "boun":
                    boun = Bounds(resp[i])
                    for j in range(boun.get_num()):
                        sizes[boun.get_id(j)] = np.array([float(np.abs(boun.get_right(j)[0] - boun.get_left(j)[0])),
                                                          float(np.abs(boun.get_top(j)[1] - boun.get_bottom(j)[1])),
                                                          float(np.abs(boun.get_front(j)[2] - boun.get_back(j)[2]))])
                elif r_id == "srig":
                    srig = StaticRigidbodies(resp[i])
                    for j in range(srig.get_num()):
                        static_rigidbodies[srig.get_id(j)] = _StaticRigidbody(mass=srig.get_mass(j),
                                                                              kinematic=srig.get_kinematic(j),
                                                                              dynamic_friction=srig.get_dynamic_friction(j),
                                                                              static_friction=srig.get_static_friction(j),
                                                                              bounciness=srig.get_bounciness(j))
                elif r_id == "cate":
                    cate = Categories(resp[i])
                    for j in range(cate.get_num_categories()):
                        self.categories[cate.get_category_name(j)] = np.array(cate.get_category_color(j))
            # Cache the sorted data.
            for object_id in segmentation_colors:
                self.objects_static[object_id] = ObjectStatic(object_id=object_id,
                                                              name=names[object_id],
                                                              segmentation_color=segmentation_colors[object_id],
                                                              mass=static_rigidbodies[object_id].mass,
                                                              kinematic=static_rigidbodies[object_id].kinematic,
                                                              dynamic_friction=static_rigidbodies[object_id].dynamic_friction,
                                                              static_friction=static_rigidbodies[object_id].static_friction,
                                                              bounciness=static_rigidbodies[object_id].bounciness,
                                                              size=sizes[object_id],
                                                              category=categories[object_id])
        # Set dynamic data.
        self.transforms.clear()
        self.rigidbodies.clear()
        self.bounds.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "tran":
                tran = Transforms(resp[i])
                for j in range(tran.get_num()):
                    self.transforms[tran.get_id(j)] = Transform(position=tran.get_position(j),
                                                                rotation=tran.get_rotation(j),
                                                                forward=tran.get_forward(j))
            elif r_id == "rigi":
                rigi = Rigidbodies(resp[i])
                for j in range(rigi.get_num()):
                    self.rigidbodies[rigi.get_id(j)] = Rigidbody(velocity=rigi.get_velocity(j),
                                                                 angular_velocity=rigi.get_angular_velocity(j),
                                                                 sleeping=rigi.get_sleeping(j))
            elif r_id == "boun":
                boun = Bounds(resp[i])
                for j in range(boun.get_num()):
                    self.bounds[boun.get_id(j)] = Bound(front=boun.get_front(j),
                                                        back=boun.get_back(j),
                                                        left=boun.get_left(j),
                                                        right=boun.get_right(j),
                                                        top=boun.get_top(j),
                                                        bottom=boun.get_bottom(j),
                                                        center=boun.get_center(j))

    def reset(self) -> None:
        """
        Reset the cached static data. Call this when resetting the scene.
        """

        self._cached_static_data = False
        self.objects_static.clear()
        self.categories.clear()
        self.initialized = False
