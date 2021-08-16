from typing import Dict, List
import numpy as np
from tdw.output_data import OutputData, Transforms, Rigidbodies, Bounds, SegmentationColors, Categories
from tdw.add_ons.add_on import AddOn
from tdw.object_data.object_static import ObjectStatic
from tdw.object_data.transform import Transform
from tdw.object_data.rigidbody import Rigidbody
from tdw.object_data.bound import Bound


class ObjectManager(AddOn):
    def __init__(self, transforms: bool = True, rigidbodies: bool = False, bounds: bool = False):
        """
        (no parameters)
        """

        super().__init__()
        self._cached_static_data: bool = False
        self._send_transforms: str = "always" if transforms else "never"
        self._send_rigidbodies: str = "always" if rigidbodies else "once"
        self._send_bounds: str = "always" if bounds else "once"
        """:field
        [Static object data per object.](../object_data/object_static.md) Key = The ID of the object.
        """
        self.objects_static: Dict[int, ObjectStatic] = dict()
        """:field
        The segmentation color per category as use in the _category image pass. Key = The category.
        """
        self.categories: Dict[str, np.array] = dict()
        """:field
        The [transform data](../object_data/transform.md) for each object on the scene on this frame. Key = The object ID. If `transforms=False` in the constructor, this dictionary will be empty.
        """
        self.transforms: Dict[int, Transform] = dict()
        self.rigidbodies: Dict[int, Rigidbody] = dict()
        self.bounds: Dict[int, Bound] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_categories"},
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
            masses: Dict[int, float] = dict()
            kinematics: Dict[int, bool] = dict()
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
                elif r_id == "boun":
                    boun = Bounds(resp[i])
                    for j in range(boun.get_num()):
                        sizes[boun.get_id(j)] = np.array([float(np.abs(boun.get_right(j)[0] - boun.get_left(j)[0])),
                                                          float(np.abs(boun.get_top(j)[1] - boun.get_bottom(j)[1])),
                                                          float(np.abs(boun.get_front(j)[2] - boun.get_back(j)[2]))])
                elif r_id == "rigi":
                    rigi = Rigidbodies(resp[i])
                    for j in range(rigi.get_num()):
                        object_id = rigi.get_id(j)
                        masses[object_id] = rigi.get_mass(j)
                        kinematics[object_id] = rigi.get_kinematic(j)
                elif r_id == "cate":
                    cate = Categories(resp[i])
                    for j in range(cate.get_num_categories()):
                        self.categories[cate.get_category_name(j)] = np.array(cate.get_category_color(j))
                    for j in range(cate.get_num_objects()):
                        categories[cate.get_object_id(j)] = cate.get_object_category(j)
            # Cache the sorted data.
            for object_id in segmentation_colors:
                self.objects_static[object_id] = ObjectStatic(object_id=object_id,
                                                              name=names[object_id],
                                                              segmentation_color=segmentation_colors[object_id],
                                                              mass=masses[object_id],
                                                              kinematic=kinematics[object_id],
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
                    self.transforms[tran.get_id(j)] = Transform(position=np.array(tran.get_position(j)),
                                                                rotation=np.array(tran.get_rotation(j)),
                                                                forward=np.array(tran.get_forward(j)))
            elif r_id == "rigi":
                rigi = Rigidbodies(resp[i])
                for j in range(rigi.get_num()):
                    self.rigidbodies[rigi.get_id(j)] = Rigidbody(velocity=rigi.get_velocity(j),
                                                                 angular_velocity=rigi.get_angular_velocity(j),
                                                                 sleeping=rigi.get_sleeping(j))
            elif r_id == "boun":
                boun = Bounds(resp[i])
                for j in range(boun.get_num()):
                    self.bounds[boun.get_id(j)] = Bound(front=np.array(boun.get_front(j)),
                                                        back=np.array(boun.get_back(j)),
                                                        left=np.array(boun.get_left(j)),
                                                        right=np.array(boun.get_right(j)),
                                                        top=np.array(boun.get_top(j)),
                                                        bottom=np.array(boun.get_bottom(j)),
                                                        center=np.array(boun.get_center(j)))

    def reset(self) -> None:
        """
        Reset the cached static data. Call this when resetting the scene.
        """

        self._cached_static_data = False
        self.objects_static.clear()
        self.categories.clear()
