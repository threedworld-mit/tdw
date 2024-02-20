from typing import Dict, List, Tuple, Optional
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Raycast
from tdw.librarian import ModelLibrarian
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.container_shape import ContainerShape
from tdw.container_data.box_container import BoxContainer
from tdw.container_data.cylinder_container import CylinderContainer
from tdw.container_data.sphere_container import SphereContainer


class ContainerCacher(Controller):
    """
    Add objects and raycast in order to define container shapes for different shapes, for example basket interiors or table surfaces.
    """

    SURFACE_COLLIDER_HEIGHT: float = 0.01
    Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
    Controller.MODEL_LIBRARIANS["models_full.json"] = ModelLibrarian("models_full.json")

    def __init__(self, launch_build: bool = True, log: bool = True):
        super().__init__(launch_build=launch_build)
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self._record_log: bool = log
        self.log: List[str] = list()

    def box_cavity(self, model_name: str) -> Optional[BoxContainer]:
        """
        Find a cavity in the center of a model, for example the interior of a basket.

        :param model_name: The model name.

        :return: A BoxContainer. Can be None. Tag: "inside".
        """

        hit, object_id, bottom_y = self._add_object_and_raycast_down(model_name=model_name)
        # Failed to hit the object.
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to get cavity because raycast failed to hit {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return None
        # Raycast cardinal directions.
        resp = self._raycast_in_cardinal_directions_from_origin(origin={"x": 0, "y": bottom_y + 0.01, "z": 0})
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions for cavity in {model_name}.")
            return None
        # Get the record and the extents.
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        width = np.linalg.norm(points[2] - points[8])
        height = extents[1] - bottom_y
        length = np.linalg.norm(points[1] - points[4])
        if self._record_log:
            self.log.append(f"Got cavity for {model_name}.")
        # Get the collider.
        return BoxContainer(tag=ContainerTag.inside,
                            position={"x": 0, "y": bottom_y + height / 2, "z": 0},
                            half_extents={"x": width / 2, "y": height / 2, "z": length / 2},
                            rotation=TDWUtils.VECTOR3_ZERO)

    def interior_box_cavity(self, model_name: str, origin: Dict[str, float] = None) -> Optional[BoxContainer]:
        """
        Find a box cavity in the interior of a model, for example the interior of a microwave.

        :param model_name: The model name.
        :param origin: The origin. If None, a default origin is used.

        :return: A BoxContainer. Can be None. Tag: "enclosed".
        """

        object_id = self.get_unique_id()
        # Add the object.
        self.communicate(Controller.get_add_physics_object(model_name=model_name,
                                                           object_id=object_id,
                                                           kinematic=True))
        if origin is None:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
            extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
            origin = {"x": 0, "y": extents[1] / 2, "z": 0}
        # Raycast cardinal directions.
        resp = self._raycast_in_cardinal_directions_from_origin(origin=origin)
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions for interior box cavity in {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return None
        # Raycast up and down.
        resp = self.communicate([{"$type": "send_raycast",
                                  "origin": origin,
                                  "destination": {"x": origin["x"],
                                                  "y": origin["y"] + 1000,
                                                  "z": origin["z"]},
                                  "id": 0},
                                 {"$type": "send_raycast",
                                  "origin": origin,
                                  "destination": {"x": origin["x"],
                                                  "y": origin["y"] - 1000,
                                                  "z": origin["z"]},
                                  "id": 1}])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        up = np.array([0, 0, 0])
        down = np.array([0, 0, 0])
        for i in range(len(resp) - 1):
            raycast = Raycast(resp[i])
            if not raycast.get_hit() or not raycast.get_hit_object():
                if self._record_log:
                    self.log.append(f"Failed to raycast up and down for interior box cavity in {model_name}.")
                return None
            raycast_id = raycast.get_raycast_id()
            if raycast_id == 0:
                up = np.array(raycast.get_point())
            else:
                down = np.array(raycast.get_point())
        # Get the midpoint and height.
        width = np.linalg.norm(points[2] - points[8])
        height = np.linalg.norm(up - down)
        length = np.linalg.norm(points[1] - points[4])
        if self._record_log:
            self.log.append(f"Got interior box cavity for {model_name}.")
        # Get the collider.
        return BoxContainer(tag=ContainerTag.enclosed,
                            position={"x": (points[2][0] + points[8][0]) / 2,
                                      "y": (up[1] + down[1]) / 2,
                                      "z": (points[1][2] + points[4][2]) / 2},
                            half_extents={"x": width / 2, "y": height / 2, "z": length / 2},
                            rotation=TDWUtils.VECTOR3_ZERO)

    def cylinder_cavity(self, model_name: str) -> Optional[CylinderContainer]:
        """
        Find a cylinder cavity in the center of a model, for example the interior of a pot.

        :param model_name: The model name.

        :return: A CylinderContainer. Can be None. Tag: "inside".
        """

        hit, object_id, bottom_y = self._add_object_and_raycast_down(model_name=model_name)
        # Failed to hit the object.
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to get cylinder cavity because raycast failed to hit {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return None
        # Get the record and the extents.
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        # If we hit close to the top of the object, ignore it.
        if extents[1] - bottom_y < 0.05:
            if self._record_log:
                self.log.append(f"Failed to get cylinder cavity to {model_name} because the raycast hit close to the top of the object.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return None
        # Raycast cardinal directions.
        resp = self._raycast_in_cardinal_directions_from_origin(origin={"x": 0, "y": bottom_y + extents[1] / 2, "z": 0})
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        # Get the raycast points.
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions for cylinder cavity in {model_name}.")
            return None
        height = extents[1] - bottom_y
        # Get the radius from the width and length.
        if self._record_log:
            self.log.append(f"Got cylinder cavity for {model_name}.")
        # Get the collider.
        return CylinderContainer(tag=ContainerTag.inside,
                                 position={"x": (points[2][0] + points[8][0]) / 2,
                                           "y": bottom_y + height / 2,
                                           "z": (points[1][2] + points[4][2]) / 2},
                                 radius=np.linalg.norm(points[2] - points[8]) / 2,
                                 height=float(height),
                                 rotation=TDWUtils.VECTOR3_ZERO)

    def interior_cylinder_cavity(self, model_name: str) -> Optional[CylinderContainer]:
        """
        Find a half-height cylinder cavity in the interior of a model, for example the interior of a vase.

        :param model_name: The model name.

        :return: A CylinderContainer. Can be None. Tag: "inside".
        """

        container = self.cylinder_cavity(model_name=model_name)
        if container is None:
            return container
        else:
            container.height /= 2
            container.position["y"] -= container.height / 2
            return container

    def enclosed_cylinder_cavity(self, model_name) -> Optional[CylinderContainer]:
        """
        Find a cylinder cavity in the interior of an enclosed model, for example a pot with a lid.

        :param model_name: The model name.

        :return: A CylinderContainer. Can be None. Tag: "inside".
        """

        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        object_id = self.get_unique_id()
        # Add the object.
        commands = Controller.get_add_physics_object(model_name=model_name,
                                                     object_id=object_id,
                                                     kinematic=True)
        # Raycast up and down.
        origin = {"x": 0, "y": extents[1] / 2, "z": 0}
        commands.extend([{"$type": "send_raycast",
                          "origin": origin,
                          "destination": {"x": 0, "y": 100, "z": 0},
                          "id": 0},
                         {"$type": "send_raycast",
                          "origin": origin,
                          "destination": {"x": 0, "y": -100, "z": 0},
                          "id": 1}])
        resp = self.communicate(commands)
        up = (0, 0, 0)
        down = (0, 0, 0)
        for i in range(len(resp) - 1):
            raycast = Raycast(resp[i])
            if not raycast.get_hit() or not raycast.get_hit_object():
                if self._record_log:
                    self.log.append(f"Failed to get height of cylinder cavity because raycast failed to hit {model_name}.")
                # Destroy the object.
                self.communicate({"$type": "destroy_object",
                                  "id": object_id})
                return None
            if raycast.get_raycast_id() == 0:
                up = raycast.get_point()
            else:
                down = raycast.get_point()
        # Raycast cardinal directions.
        resp = self._raycast_in_cardinal_directions_from_origin(origin=origin)
        # Get the raycast points.
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions for cylinder cavity in {model_name}.")
            return None
        if self._record_log:
            self.log.append(f"Got cylinder cavity for {model_name}.")
        width = np.linalg.norm(points[2] - points[8])
        height = up[1] - down[1]
        return CylinderContainer(position={"x": 0, "y": (up[1] + down[1]) / 2, "z": 0},
                                 radius=width / 2,
                                 height=height,
                                 tag=ContainerTag.inside,
                                 rotation=TDWUtils.VECTOR3_ZERO)

    def interior_sphere_cavity(self, model_name: str, y_factor: float) -> Optional[SphereContainer]:
        """
        Add an interior sphere cavity.
        
        :param model_name: The model name.
        :param y_factor: Offset the y coordinate of the center of the sphere by this factor.

        :return: A SphereContainer. Can be None. Tag: "inside".
        """

        hit, object_id, bottom_y = self._add_object_and_raycast_down(model_name=model_name)
        # Failed to hit the object.
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to get sphere cavity because raycast failed to hit {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return None
        # Get the record and the extents.
        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        # If we hit close to the top of the object, ignore it.
        if extents[1] - bottom_y < 0.05:
            if self._record_log:
                self.log.append(f"Failed to get sphere cavity to {model_name} because the raycast hit close to the top of the object.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return None
        position = {"x": 0, "y": (extents[1] - bottom_y) * y_factor, "z": 0}
        # Raycast cardinal directions.
        resp = self._raycast_in_cardinal_directions_from_origin(origin=position)
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        # Get the raycast points.
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions for sphere cavity in {model_name}.")
            return None
        if self._record_log:
            self.log.append(f"Got sphere cavity for {model_name}.")
        return SphereContainer(tag=ContainerTag.inside,
                               position=position,
                               radius=min([np.linalg.norm(points[2] - points[8]),
                                           np.linalg.norm(points[1] - points[4])]) / 2)

    def rectangular_surface(self, model_name: str) -> Optional[BoxContainer]:
        """
        Find the rectangular surface of an object, such as a table top.

        :param model_name: The model name.

        :return: A BoxContainer. Can be None. Tag: "on".
        """

        got_points, top_y, points = self._get_rectangular_surface_raycast_points(model_name=model_name)
        if got_points:
            return BoxContainer(tag=ContainerTag.on,
                                position={"x": (points[2][0] + points[8][0]) / 2,
                                          "y": top_y + ContainerCacher.SURFACE_COLLIDER_HEIGHT / 2,
                                          "z": (points[1][2] + points[4][2]) / 2},
                                half_extents={"x": np.linalg.norm(points[2] - points[8]) / 2,
                                              "y": ContainerCacher.SURFACE_COLLIDER_HEIGHT / 2,
                                              "z": np.linalg.norm(points[1] - points[4]) / 2},
                                rotation=TDWUtils.VECTOR3_ZERO)
        else:
            return None

    def circular_surface(self, model_name: str) -> Optional[CylinderContainer]:
        """
        Find the circular surface of an object, such as a circular table top.

        :param model_name: The model name.

        :return: A CylinderContainer. Can be None. Tag: "on".
        """

        got_points, top_y, points = self._get_rectangular_surface_raycast_points(model_name=model_name)
        if got_points:
            return CylinderContainer(tag=ContainerTag.on,
                                     position={"x": (points[2][0] + points[8][0]) / 2,
                                               "y": top_y + ContainerCacher.SURFACE_COLLIDER_HEIGHT / 2,
                                               "z": (points[1][2] + points[4][2]) / 2},
                                     radius=np.linalg.norm(points[2] - points[8]) / 2,
                                     height=ContainerCacher.SURFACE_COLLIDER_HEIGHT,
                                     rotation=TDWUtils.VECTOR3_ZERO)
        else:
            return None

    def shelves(self, model_name: str, ys: List[float]) -> List[BoxContainer]:
        """
        Get shelves as a list of container shapes.
        This function doesn't require the controller to send commands.

        :param model_name: The model name.
        :param ys: A list of pre-defined y values for the shelves, including the top of the model.

        :return: A list of container shapes.
        """

        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        if self._record_log:
            self.log.append(f"Got shelves for {model_name}.")
        return [BoxContainer(tag=ContainerTag.on,
                             position={"x": 0,
                                       "y": y + ContainerCacher.SURFACE_COLLIDER_HEIGHT / 2,
                                       "z": 0},
                             half_extents={"x": extents[0] / 2,
                                           "y": ContainerCacher.SURFACE_COLLIDER_HEIGHT,
                                           "z": extents[2] / 2},
                             rotation=TDWUtils.VECTOR3_ZERO) for y in ys]

    def sink(self, model_name: str) -> List[BoxContainer]:
        """
        Get container shapes for the sink: One in the basin, two on the left and right counters, and one inside.

        :param model_name: The model name.

        :return: A list of containers.
        """

        record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
        hit, object_id, sink_basin_y = self._add_object_and_raycast_down(model_name=model_name)
        # Failed to hit the object.
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to get sink basin because raycast failed to hit {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return []
        # Raycast cardinal directions.
        resp = self._raycast_in_cardinal_directions_from_origin(origin={"x": 0, "y": sink_basin_y + 0.1, "z": 0})
        # Get the raycast points.
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions {model_name}'s sink basin.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return []
        if self._record_log:
            self.log.append(f"Got {model_name}'s sink basin and surfaces.")
        # Add a collider in the basin and two containers for the surfaces.
        surface_scale = {"x": ((extents[0] / 2) - points[2][0]) * 0.4,
                         "y": ContainerCacher.SURFACE_COLLIDER_HEIGHT,
                         "z": extents[2] / 2}
        containers = [BoxContainer(tag=ContainerTag.inside,
                                   position={"x": 0,
                                             "y": sink_basin_y + (extents[1] - sink_basin_y) / 2,
                                             "z": 0},
                                   half_extents={"x": np.linalg.norm(points[2] - points[8]) / 2,
                                                 "y": (extents[1] - sink_basin_y) / 2,
                                                 "z": np.linalg.norm(points[1] - points[4]) / 2},
                                   rotation=TDWUtils.VECTOR3_ZERO),
                      BoxContainer(tag=ContainerTag.on,
                                   position={"x": (extents[0] - points[2][0]) * 0.47,
                                             "y": extents[1],
                                             "z": 0},
                                   half_extents=surface_scale,
                                   rotation=TDWUtils.VECTOR3_ZERO),
                      BoxContainer(tag=ContainerTag.on,
                                   position={"x": (-extents[0] / 2 + points[8][0]) * 0.53,
                                             "y": extents[1],
                                             "z": 0},
                                   half_extents=surface_scale,
                                   rotation=TDWUtils.VECTOR3_ZERO)]
        # Add the interior collider.
        trigger_collider = self.interior_box_cavity(model_name=model_name)
        if trigger_collider is not None:
            containers.append(trigger_collider)
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return containers

    def interior_cavity_with_divider(self, model_name: str,
                                     cavity_positions: List[Dict[str, float]]) -> List[BoxContainer]:
        """
        :param model_name: The name.

        :param cavity_positions: The approximate center positions of each cavity box collider (they will be corrected).

        :return: A list of containers: One on the surface and n interior cavity containers.
        """

        hit, object_id, sink_basin_y = self._add_object_and_raycast_down(model_name=model_name)
        # Failed to hit the object.
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast failed to hit {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return []
        containers = []
        trigger_collider = self.rectangular_surface(model_name=model_name)
        if trigger_collider is not None:
            containers.append(trigger_collider)
        for cavity_position in cavity_positions:
            trigger_collider = self.interior_box_cavity(model_name=model_name, origin=cavity_position)
            if trigger_collider is not None:
                containers.append(trigger_collider)
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return containers

    @staticmethod
    def update_record(model_name: str, containers: List[ContainerShape], write: bool) -> None:
        """
        Update a record with new container shapes.

        :param model_name: The model name.
        :param containers: The new containers.
        :param write: If True, write the json file.
        """

        for lib in Controller.MODEL_LIBRARIANS.values():
            record = lib.get_record(model_name)
            if record is not None:
                record.container_shapes.extend(containers)
                lib.add_or_update_record(record=record, overwrite=True, write=write)

    def _show_containers(self, object_id: int, containers: List[ContainerShape]) -> None:
        commands = []
        for i, container in enumerate(containers):
            if isinstance(container, SphereContainer):
                diameter = container.radius * 2
                scale = {"x": diameter, "y": diameter, "z": diameter}
                shape = "sphere"
            elif isinstance(container, BoxContainer):
                scale = {k: v * 2 for k, v in container.half_extents.items()}
                shape = "box"
            elif isinstance(container, CylinderContainer):
                scale = {"x": container.radius * 2, "y": container.height, "z": container.radius * 2}
                shape = "cylinder"
            else:
                raise Exception(container)
            commands.append({"$type": "add_trigger_collider",
                             "id": object_id,
                             "shape": shape,
                             "trigger_id": i,
                             "scale": scale,
                             "position": container.position})
        self.communicate(commands)

    def _add_object_and_raycast_down(self, model_name: str) -> Tuple[bool, int, float]:
        """
        Add an object and raycast down to get its "top" point.

        :param model_name: The model name.

        :return: Tuple: True if the raycast hit the object, the object ID, the y value.
        """

        object_id = self.get_unique_id()
        # Add the object.
        commands = Controller.get_add_physics_object(model_name=model_name,
                                                     object_id=object_id,
                                                     kinematic=True)
        # Raycast down.
        commands.append({"$type": "send_raycast",
                         "origin": {"x": 0, "y": 100, "z": 0},
                         "destination": {"x": 0, "y": -100, "z": 0}})
        resp = self.communicate(commands)
        raycast = Raycast(resp[0])
        if not raycast.get_hit() or not raycast.get_hit_object():
            return False, -1, -1
        else:
            return True, object_id, raycast.get_point()[1]

    @staticmethod
    def _get_cardinal_direction_raycast_points(resp: List[bytes]) -> Tuple[bool, Dict[int, np.array]]:
        """
        Parse 4 raycasts that were sent in cardinal directions.

        :param resp: The response from the build.
        :return: Tuple: True if all of the raycasts hit, a dictionary of points where the key is the raycast ID.
        """

        points: Dict[int, np.array] = dict()
        for i in range(len(resp) - 1):
            raycast = Raycast(resp[i])
            raycast_id = raycast.get_raycast_id()
            if not raycast.get_hit() or not raycast.get_hit_object():
                return False, points
            points[raycast_id] = np.array(raycast.get_point())
        return True, points

    def _raycast_in_cardinal_directions_from_origin(self, origin: Dict[str, float]) -> List[bytes]:
        """
        Raycast in cardinal directions (north, south, east, west) from an origin position.

        :param origin: The origin position.
        :return: The response from the build.
        """

        return self.communicate([{"$type": "send_raycast",
                                  "origin": origin,
                                  "destination": {"x": origin["x"],
                                                  "y": origin["y"],
                                                  "z": origin["z"] + 1000},
                                  "id": 1},
                                 {"$type": "send_raycast",
                                  "origin": origin,
                                  "destination": {"x": origin["x"] + 1000,
                                                  "y": origin["y"],
                                                  "z": origin["z"]},
                                  "id": 2},
                                 {"$type": "send_raycast",
                                  "origin": origin,
                                  "destination": {"x": origin["x"],
                                                  "y": origin["y"],
                                                  "z": origin["z"] - 1000},
                                  "id": 4},
                                 {"$type": "send_raycast",
                                  "origin": origin,
                                  "destination": {"x": origin["x"] - 1000,
                                                  "y": origin["y"],
                                                  "z": origin["z"]},
                                  "id": 8}])

    def _raycast_from_cardinal_directions_to_destination(self, destination: Dict[str, float]) -> List[bytes]:
        """
        Raycast from cardinal directions surrounding the object to a destination point.

        :param destination: The raycast destination.

        :return: The response from the build.
        """

        return self.communicate([{"$type": "send_raycast",
                                  "origin": {"x": 0, "y": destination["y"], "z": 4},
                                  "destination": destination,
                                  "id": 1},
                                 {"$type": "send_raycast",
                                  "origin": {"x": 4, "y": destination["y"], "z": 0},
                                  "destination": destination,
                                  "id": 2},
                                 {"$type": "send_raycast",
                                  "origin": {"x": 0, "y": destination["y"], "z": -4},
                                  "destination": destination,
                                  "id": 4},
                                 {"$type": "send_raycast",
                                  "origin": {"x": -4, "y": destination["y"], "z": 0},
                                  "destination": destination,
                                  "id": 8}])

    def _get_rectangular_surface_raycast_points(self, model_name: str) -> Tuple[bool, float, Dict[int, np.array]]:
        """
        :param model_name: The model name.

        :return: Tuple: True if there are points, the top y value, the cardinal direction raycast points for a rectangular surface.
        """

        # Add object and raycast to get the top of the object.
        hit, object_id, top_y = self._add_object_and_raycast_down(model_name=model_name)
        # Failed to hit the object.
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to get rectangular surface because raycast failed to hit {model_name}.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return False, -1, dict()
        # Raycast just below the top.
        raycast_y = top_y - 0.001
        if raycast_y < 0:
            record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
            extents = TDWUtils.get_bounds_extents(bounds=record.bounds)
            raycast_y = extents[1] / 2
        # This is a very thin object and the raycasts will go below the floor.
        if raycast_y < 0:
            if self._record_log:
                self.log.append(
                    f"Failed to get rectangular surface for {model_name} because cardinal direction raycasts would be y < 0.")
            # Destroy the object.
            self.communicate({"$type": "destroy_object",
                              "id": object_id})
            return False, -1, dict()
        # Raycast towards the destination. This will tell us the "true" dimensions of the surface.
        # For example, this will exclude the dimensions of a door handle from a cabinet.
        resp = self._raycast_from_cardinal_directions_to_destination(destination={"x": 0, "y": raycast_y, "z": 0})
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        # Get the raycast points.
        hit, points = ContainerCacher._get_cardinal_direction_raycast_points(resp=resp)
        if not hit:
            if self._record_log:
                self.log.append(f"Failed to raycast cardinal directions for rectangular surface for {model_name}.")
            return False, -1, dict()
        if self._record_log:
            self.log.append(f"Got rectangular surface for {model_name}.")
        return True, top_y, points
