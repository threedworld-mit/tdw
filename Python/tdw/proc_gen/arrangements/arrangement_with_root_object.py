from typing import Dict, List, Union, Optional
from abc import ABC, abstractmethod
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from overrides import final
import numpy as np
from tdw.librarian import ModelRecord, ModelLibrarian
from tdw.controller import Controller
from tdw.proc_gen.arrangements.arrangement import Arrangement
from tdw.container_data.container_trigger_collider import ContainerTriggerCollider
from tdw.container_data.container_box_trigger_collider import ContainerBoxTriggerCollider
from tdw.container_data.container_cylinder_trigger_collider import ContainerCylinderTriggerCollider
from tdw.container_data.container_sphere_trigger_collider import ContainerSphereTriggerCollider
from tdw.container_data.container_collider_tag import ContainerColliderTag


class ArrangementWithRootObject(Arrangement, ABC):
    """
    Abstract class for procedurally-generated spatial arrangements of objects with a single root object.
    """

    """:class_var
    A dictionary of categories that can be on top of other categories. Key = A category. Value = A list of categories of models that can be on top of the key category.
    """
    ON_TOP_OF: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "data/on_top_of.json")).read_text())
    """:class_var
    A dictionary of categories that can be enclosed by other categories. Key = A category. Value = A list of categories of models that can enclosed by the key category.
    """
    ENCLOSED_BY: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "data/enclosed_by.json")).read_text())
    """:class_var
    A dictionary of categories that can be inside of other categories. Key = A category. Value = A list of categories of models that can inside of the key category.
    """
    INSIDE_OF: Dict[str, List[str]] = loads(Path(resource_filename(__name__, "data/inside_of.json")).read_text())

    def __init__(self, position: Dict[str, float], model: Union[str, ModelRecord] = None, rng: np.random.RandomState = None):
        """
        :param position: The position of the root object. This might be adjusted.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a random model is selected.
        :param rng: The random number generator. If None, a new random number generator is created.
        """

        if "models_core.json" not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian()
        # Choose a random record.
        if model is None:
            if rng is None:
                rng = np.random.RandomState()
            category = self._get_category()
            if category not in Arrangement.MODEL_CATEGORIES:
                self._record: Optional[ModelRecord] = None
            else:
                model_names = Arrangement.MODEL_CATEGORIES[category]
                model_name = model_names[rng.randint(0, len(model_names))]
                self._record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        # Get the record.
        elif isinstance(model, str):
            self._record: Optional[ModelRecord] = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model)
        # This is a record.
        elif isinstance(model, ModelRecord):
            self._record = model
        else:
            raise Exception(f"Invalid model parameter: {model}")
        """:field
        The ID of the root object.
        """
        self.root_object_id: int = Controller.get_unique_id()
        super().__init__(position=position, rng=rng)
        self.object_ids.append(self.root_object_id)

    @final
    def _add_root_object(self, kinematic: bool = True) -> List[dict]:
        """
        :param kinematic: If True, the root object is kinematic.

        :return: A list of commands to add the root object.
        """

        return Controller.get_add_physics_object(model_name=self._record.name,
                                                 object_id=self.root_object_id,
                                                 position=self._position,
                                                 library="models_core.json",
                                                 kinematic=kinematic)

    @final
    def _add_object_with_other_objects_on_top(self, density: float = 0.4, cell_size: float = 0.05,
                                              rotate: bool = True, kinematic: bool = True,
                                              x_scale: float = 0.8, z_scale: float = 0.8) -> List[dict]:
        """
        Add the root object and add objects on top of it.

        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.
        :param rotate: If True, append rotation commands.
        :param kinematic: If True, the root object is kinematic.
        :param x_scale: Scale the rectangular space along the x axis by this factor.
        :param z_scale: Scale the rectangular space along the z axis by this factor.

        :return: A list of commands.
        """

        categories: List[str] = ArrangementWithRootObject.ON_TOP_OF[self._get_category()]
        commands = self._add_root_object(kinematic=kinematic)
        for collider in self._record.container_colliders:
            # Use all of the "on" colliders.
            if collider.tag == ContainerColliderTag.on:
                if isinstance(collider, ContainerBoxTriggerCollider):
                    scale = collider.scale
                elif isinstance(collider, ContainerCylinderTriggerCollider):
                    scale = collider.scale
                else:
                    raise Exception(collider)
                # Add objects on top of the root object.
                on_top_commands, object_ids = self._add_rectangular_arrangement(size=(scale["x"] * x_scale,
                                                                                      scale["z"] * z_scale),
                                                                                categories=categories,
                                                                                position=self._get_collider_position(collider=collider),
                                                                                cell_size=cell_size,
                                                                                density=density)
                commands.extend(on_top_commands)
        # Rotate everything.
        if rotate:
            commands.extend(self._get_rotation_commands())
        return commands

    def _add_enclosed_objects(self, density: float = 0.4, cell_size: float = 0.05, rotate: bool = True,
                              x_scale: float = 0.8, z_scale: float = 0.8) -> List[dict]:
        """
        Add objects enclosed by the root object.

        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.
        :param rotate: If True, append rotation commands.
        :param x_scale: Scale the rectangular space along the x axis by this factor.
        :param z_scale: Scale the rectangular space along the z axis by this factor.

        :return: A list of commands.
        """

        categories: List[str] = ArrangementWithRootObject.ENCLOSED_BY[self._get_category()]
        commands = []
        for collider in self._record.container_colliders:
            # Use all of the "enclosed" colliders.
            if collider.tag == ContainerColliderTag.enclosed:
                if isinstance(collider, ContainerBoxTriggerCollider):
                    scale = collider.scale
                else:
                    raise Exception(collider)
                # Add objects on top of the root object.
                on_top_commands, object_ids = self._add_rectangular_arrangement(size=(scale["x"] * x_scale,
                                                                                      scale["z"] * z_scale),
                                                                                categories=categories,
                                                                                position=self._get_collider_position(collider=collider),
                                                                                cell_size=cell_size,
                                                                                density=density)
                commands.extend(on_top_commands)
        # Rotate everything.
        if rotate:
            commands.extend(self._get_rotation_commands())
        return commands

    def _add_inside_objects(self, density: float = 0.4, cell_size: float = 0.05, rotate: bool = True,
                            x_scale: float = 0.8, z_scale: float = 0.8) -> List[dict]:
        """
        Add objects inside of the root object.

        :param density: The probability of a "cell" in the arrangement being empty. Lower value = a higher density of small objects.
        :param cell_size: The size of each cell in the rectangle. This controls the minimum size of objects and the density of the arrangement.
        :param rotate: If True, append rotation commands.
        :param x_scale: Scale the rectangular space along the x axis by this factor.
        :param z_scale: Scale the rectangular space along the z axis by this factor.

        :return: A list of commands.
        """

        categories: List[str] = ArrangementWithRootObject.INSIDE_OF[self._get_category()]
        commands = []
        for collider in self._record.container_colliders:
            # Use all of the "enclosed" colliders.
            if collider.tag == ContainerColliderTag.inside:
                if isinstance(collider, ContainerBoxTriggerCollider):
                    scale = collider.scale
                elif isinstance(collider, ContainerCylinderTriggerCollider):
                    scale = collider.scale
                elif isinstance(collider, ContainerSphereTriggerCollider):
                    scale = {"x": collider.diameter, "y": collider.diameter, "z": collider.diameter}
                else:
                    raise Exception(collider)
                # Add objects on top of the root object.
                on_top_commands, object_ids = self._add_rectangular_arrangement(size=(scale["x"] * x_scale,
                                                                                      scale["z"] * z_scale),
                                                                                categories=categories,
                                                                                position=self._get_collider_position(collider=collider),
                                                                                cell_size=cell_size,
                                                                                density=density)
                commands.extend(on_top_commands)
        # Rotate everything.
        if rotate:
            commands.extend(self._get_rotation_commands())
        return commands

    @final
    def _get_collider_position(self, collider: ContainerTriggerCollider) -> Dict[str, float]:
        """
        :param collider: The collider.

        :return: The worldspace position of the collider.
        """

        return {"x": self._position["x"] + collider.bottom_center_position["x"],
                "y": self._position["y"] + collider.bottom_center_position["y"],
                "z": self._position["z"] + collider.bottom_center_position["z"]}

    @final
    def _get_rotation_commands(self) -> List[dict]:
        """
        :return: A list of commands to parent the child objects to the parent object, rotate the parent object, and unparent the child objects.
        """

        child_object_ids = [object_id for object_id in self.object_ids if object_id != self.root_object_id]
        commands = []
        # Parent all objects to the root object.
        for child_object_id in child_object_ids:
            commands.append({"$type": "parent_object_to_object",
                             "id": child_object_id,
                             "parent_id": self.root_object_id})
        # Rotate the root object.
        commands.append({"$type": "rotate_object_by",
                         "angle": self._rotation,
                         "id": self.root_object_id,
                         "axis": "yaw",
                         "is_world": True,
                         "use_centroid": False})
        # Unparent all of the objects from the root object.
        for child_object_id in child_object_ids:
            commands.append({"$type": "unparent_object",
                             "id": child_object_id})
        return commands

    @abstractmethod
    def _get_category(self) -> str:
        """
        :return: The category of the root object.
        """

        raise Exception()
