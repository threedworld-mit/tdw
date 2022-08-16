from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from typing import Union, Dict, List

class AffordancePoints():

    # A dictionary of affordance points per model. This could be saved to a json file.
    AFFORDANCE_POINTS = {"basket_18inx18inx12iin_wicker": [{'x': -0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0, 'y': 0.305, 'z': 0.2285},
                                                           {'x': 0, 'y': 0.305, 'z': -0.2285}],
                         "basket_18inx18inx12iin_bamboo": [{'x': -0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0.2285, 'y': 0.305, 'z': 0.0},
                                                           {'x': 0, 'y': 0.305, 'z': 0.2285},
                                                           {'x': 0, 'y': 0.305, 'z': -0.2285}]}

    # Store empty object IDs.
    # Key = The empty object ID. Value = {"object_id": object_id, "position": position}
    EMPTY_OBJECT_IDS: Dict[int, Dict[str, int]] = dict()

    AFFORDANCE_POINTS_BY_OBJECT_ID: Dict[int, Dict[int, Dict[str, float]]] = dict()

    
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
