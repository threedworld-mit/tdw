from typing import List, Dict
import numpy as np
from tdw.output_data import OutputData, SegmentationColors, StaticCompositeObjects, Overlap
from tdw.add_ons.add_on import AddOn
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.box_container import BoxContainer
from tdw.container_data.sphere_container import SphereContainer
from tdw.container_data.cylinder_container import CylinderContainer
from tdw.container_data.containment_event import ContainmentEvent
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic
from tdw.controller import Controller
from tdw.librarian import ModelLibrarian


class ContainerManager(AddOn):
    """
    Manage containment events for 'container' objects.

    'Containers' can be concave objects such as baskets but they don't have to be. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.

    An object is 'contained' by a 'container' if it overlaps with a "containment" space, for example the interior of a pot.
    """

    _NEXT_CONTAINER_ID: int = 0

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self._getting_model_names: bool = True
        """:field
        A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container shape ID (not the object ID). Value = A list of [`ContainmentEvent`](../container_data/containment_event.md) data.
        """
        self.events: Dict[int, ContainmentEvent] = dict()
        """:field
        A dictionary of container shape IDs. Key = The container shape ID. Value = The object ID.
        """
        self.container_shapes: Dict[int, int] = dict()
        """:field
        Tags describing each container shape. Key = The container shape ID. Value = [`ContainerTag`](../container_data/container_tag.md).
        """
        self.tags: Dict[int, ContainerTag] = dict()
        self._excluded_objects: List[int] = list()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_static_composite_objects"},
                {"$type": "send_containment",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        # Get model names.
        if self._getting_model_names:
            self._getting_model_names = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Use the model names from SegmentationColors output data to add container shapes.
                if r_id == "segm":
                    segmentation_colors = SegmentationColors(resp[i])
                    for j in range(segmentation_colors.get_num()):
                        object_id = segmentation_colors.get_object_id(j)
                        model_name = segmentation_colors.get_object_name(j).lower()
                        # Add the model librarians.
                        for library_path in ModelLibrarian.get_library_filenames():
                            if library_path not in Controller.MODEL_LIBRARIANS:
                                Controller.MODEL_LIBRARIANS[library_path] = ModelLibrarian(library_path)
                        # Fine the model record.
                        for library_path in Controller.MODEL_LIBRARIANS:
                            record = Controller.MODEL_LIBRARIANS[library_path].get_record(model_name)
                            if record is not None:
                                for container_shape in record.container_shapes:
                                    if isinstance(container_shape, BoxContainer):
                                        self.add_box(object_id=object_id,
                                                     position=container_shape.position,
                                                     tag=container_shape.tag,
                                                     half_extents=container_shape.half_extents,
                                                     rotation=container_shape.rotation)
                                    elif isinstance(container_shape, CylinderContainer):
                                        self.add_cylinder(object_id=object_id,
                                                          position=container_shape.position,
                                                          tag=container_shape.tag,
                                                          radius=container_shape.radius,
                                                          height=container_shape.height,
                                                          rotation=container_shape.rotation)
                                    elif isinstance(container_shape, SphereContainer):
                                        self.add_sphere(object_id=object_id,
                                                        position=container_shape.position,
                                                        tag=container_shape.tag,
                                                        radius=container_shape.radius)
                                    else:
                                        raise Exception(container_shape)
                                break
                elif r_id == "scom":
                    static_composite_objects = StaticCompositeObjects(resp[i])
                    for j in range(static_composite_objects.get_num()):
                        s = CompositeObjectStatic(static_composite_objects, j)
                        self._excluded_objects.extend(s.sub_object_ids)
        # Get containment.
        self.events.clear()
        for i in range(len(resp) - 1):
            if OutputData.get_data_type_id(resp[i]) == "over":
                overlap = Overlap(resp[i])
                overlap_id = overlap.get_id()
                # This overlap is from a container.
                if overlap_id in self.container_shapes:
                    # Get the object ID.
                    object_id = self.container_shapes[overlap_id]
                    # Get the IDs of the contained objects.
                    contained_ids = np.array([o_id for o_id in overlap.get_object_ids() if int(o_id) not in self._excluded_objects], dtype=int)
                    if len(contained_ids) > 0:
                        # Record the containment event.
                        self.events[overlap_id] = ContainmentEvent(container_id=object_id,
                                                                   object_ids=contained_ids,
                                                                   tag=self.tags[overlap_id])

    def add_box(self, object_id: int, position: Dict[str, float], tag: ContainerTag, half_extents: Dict[str, float],
                rotation: Dict[str, float]) -> int:
        """
        Add a box container shape to an object.

        :param object_id: The ID of the object.
        :param position: The position of the box relative to the parent object.
        :param tag: The box's semantic [`ContainerTag`](../container_data/container_tag.md).
        :param half_extents: The half-extents (half the scale) of the box.
        :param rotation: The rotation of the box in Euler angles relative to the parent object.

        :return: The ID of the container shape.
        """

        command = self._get_container_shape_command(command_name="add_box_container",
                                                    object_id=object_id,
                                                    position=position,
                                                    tag=tag)
        command["half_extents"] = half_extents
        command["rotation"] = rotation
        self.commands.append(command)
        return command["id"]

    def add_cylinder(self, object_id: int, position: Dict[str, float], tag: ContainerTag, radius: float,
                     height: float, rotation: Dict[str, float]) -> int:
        """
        Add a cylinder container shape to an object.

        :param object_id: The ID of the object.
        :param position: The position of the cylinder relative to the parent object.
        :param tag: The cylinder's semantic [`ContainerTag`](../container_data/container_tag.md).
        :param radius: The radius of the cylinder.
        :param height: The height of the cylinder.
        :param rotation: The rotation of the cylinder in Euler angles relative to the parent object.

        :return: The ID of the container shape.
        """

        command = self._get_container_shape_command(command_name="add_cylinder_container",
                                                    object_id=object_id,
                                                    position=position,
                                                    tag=tag)
        command["radius"] = radius
        command["height"] = height
        command["rotation"] = rotation
        self.commands.append(command)
        return command["id"]

    def add_sphere(self, object_id: int, position: Dict[str, float], tag: ContainerTag, radius: float) -> int:
        """
        Add a sphere container shape to an object.

        :param object_id: The ID of the object.
        :param position: The position of the sphere relative to the parent object.
        :param tag: The sphere's semantic [`ContainerTag`](../container_data/container_tag.md).
        :param radius: The radius of the sphere.

        :return: The ID of the container shape.
        """

        command = self._get_container_shape_command(command_name="add_sphere_container",
                                                    object_id=object_id,
                                                    position=position,
                                                    tag=tag)
        command["radius"] = radius
        self.commands.append(command)
        return command["id"]

    def reset(self) -> None:
        """
        Reset this add-on. Call this before resetting a scene.
        """

        self.initialized = False
        self.commands.clear()
        self._getting_model_names = True
        self.events.clear()
        self.tags.clear()
        self._excluded_objects.clear()
        self.container_shapes.clear()
        ContainerManager._NEXT_CONTAINER_ID = 0

    def _get_container_shape_command(self, command_name: str, object_id: int, position: Dict[str, float],
                                     tag: ContainerTag) -> dict:
        """
        :param command_name: The name of the command.
        :param object_id: The object ID.
        :param tag: The semantic tag.
        :param position: The local position of the container shape.

        :return: A partial command to add a container shape to an object.
        """

        # Get the container ID.
        container_id = ContainerManager._NEXT_CONTAINER_ID
        ContainerManager._NEXT_CONTAINER_ID += 1
        assert container_id not in self.tags, f"Tried adding {container_id} but it already exists."
        # Record the tag.
        self.tags[container_id] = tag
        # Record the object-shape association.
        self.container_shapes[container_id] = object_id
        # Return a partial command.
        return {"$type": command_name,
                "id": int(object_id),
                "container_id": int(container_id),
                "position": position}
