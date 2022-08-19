from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from typing import Union, Dict, List

class AffordancePoints():

    # A dictionary of affordance points per model. This could be saved to a json file.
    AFFORDANCE_POINTS: Dict[str, List[Dict[str, float]]] = dict()

    # Store empty object IDs.
    # Key = The empty object ID. Value = {"object_id": object_id, "position": position}
    EMPTY_OBJECT_IDS: Dict[int, Dict[str, int]] = dict()

    AFFORDANCE_POINTS_BY_OBJECT_ID: Dict[int, Dict[int, Dict[str, float]]] = dict()

    @staticmethod
    def get_add_object_with_affordance_points(model_name: str, object_id: int, position: Dict[str, float] = None,
                                              rotation: Dict[str, float] = None, library: str = "",
                                              scale_factor: Dict[str, float] = None, kinematic: bool = False,
                                              gravity: bool = True,
                                              default_physics_values: bool = True, mass: float = 1,
                                              dynamic_friction: float = 0.3,
                                              static_friction: float = 0.3, bounciness: float = 0.7) -> List[dict]:
        # Add the object with physics parameters.
        commands = Controller.get_add_physics_object(model_name=model_name, object_id=object_id, position=position,
                                                     rotation=rotation, library=library, scale_factor=scale_factor,
                                                     kinematic=kinematic, gravity=gravity,
                                                     default_physics_values=default_physics_values, mass=mass,
                                                     dynamic_friction=dynamic_friction, static_friction=static_friction,
                                                     bounciness=bounciness)
        # Add affordance points.
        if model_name in AffordancePoints.AFFORDANCE_POINTS:
            for affordance_position in AffordancePoints.AFFORDANCE_POINTS[model_name]:
                # Remember the original local positions.
                AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id] = dict()
                empty_object_id = Controller.get_unique_id()
                # Cache the mapping between empty object IDs and the ID of the parent object.
                AffordancePoints.EMPTY_OBJECT_IDS[empty_object_id] = {"object_id": object_id,
                                                                      "position": affordance_position}
                # Add a command to attach an empty object.
                commands.extend([{"$type": "attach_empty_object",
                                 "id": object_id,
                                 "empty_object_id": empty_object_id,
                                 "position": affordance_position},
                                 {"$type": "add_position_marker", 
                                  "position":  {'x': affordance_position['x'], 'y': affordance_position['y'] + 0.35, 'z': affordance_position['z']}, 
                                  "scale": 0.05, 
                                  "color": {"r": 1, "g": 0, "b": 0, "a": 1},
                                  "shape": "sphere"}])
                # Remember the position.
                AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id][empty_object_id] = affordance_position
        return commands

    
    @staticmethod
    def reset_affordance_points(object_id: int) -> List[dict]:
        """
        :param object_id: The object ID.
        
        :return: A list of commands to reset this object's affordance points.
        """
        
        if object_id not in AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID:
            return []
        commands = []
        for empty_object_id in AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id]:
            commands.extend([{"$type": "parent_empty_object",
                              "empty_object_id": empty_object_id,
                              "id": object_id},
                             {"$type": "teleport_empty_object",
                              "empty_object_id": empty_object_id,
                              "id": object_id,
                              "position": AffordancePoints.AFFORDANCE_POINTS_BY_OBJECT_ID[object_id][empty_object_id],
                              "absolute": False}])
        return commands
