from typing import Optional, Dict
import numpy as np
from tdw.collision_data.collision_base import CollisionBase
from tdw.collision_data.collision_obj_obj import CollisionObjObj
from tdw.collision_data.collision_obj_env import CollisionObjEnv
from tdw.object_data.rigidbody import Rigidbody
from tdw.physics_audio.collision_audio_type import CollisionAudioType
from tdw.physics_audio.object_audio_static import ObjectAudioStatic


class CollisionAudioEvent:
    """
    This class is used only in PyImpact, which has been deprecated. See: [`Clatter`](../add_ons/clatter.md).

    Data for a collision audio event.
    Includes collision data as well as the "primary" and "secondary" objects and the type of audio event.
    """

    """:class_var
    If the angular velocity is this or greater, the event is a roll, not a scrape.
    """
    ROLL_ANGULAR_VELOCITY: float = 0.5
    """:class_var
    If the area of the collision increases by at least this factor during a stay event, the collision is actually an impact.
    """
    IMPACT_AREA_RATIO: float = 5
    """:class_var
    On a stay event, if the previous area is None and the current area is greater than this, the collision is actually an impact. 
    """
    IMPACT_AREA_NEW_COLLISION: float = 1e-5

    def __init__(self, collision: CollisionBase, object_0_static: ObjectAudioStatic, object_0_dynamic: Rigidbody,
                 previous_areas: Dict[int, float], object_1_static: ObjectAudioStatic = None,
                 object_1_dynamic: Rigidbody = None):
        """
        :param collision: [The collision data.](../collision_data/collision_base.md)
        :param object_0_static: [Static data](object_audio_static.md) for the first object.
        :param object_0_dynamic: [Dynamic data](../object_data/rigidbody.md) for the first object.
        :param previous_areas: Areas of collisions from the previous frame.
        :param object_1_static: [Static data](object_audio_static.md) for the second object. If this is an environment collision, the value of this parameter should be `None`.
        :param object_1_dynamic: [Dynamic data](../object_data/rigidbody.md) for the second object. If this is an environment collision, the value of this parameter should be `None`.
        """

        """:field
        [The collision data.](../collision_data/collision_base.md)
        """
        self.collision: CollisionBase = collision
        """:field
        The area of the collision contact points.
        """
        self.area: float = 0
        """:field
        [The collision audio event type.](collision_audio_type.md)
        """
        self.collision_type: CollisionAudioType = CollisionAudioType.none
        """:field
        The ID of the primary object.
        """
        self.primary_id: int = object_0_static.object_id
        """:field
        The ID of the secondary object. If this is an environment collision, the value of this field is `None`.
        """
        self.secondary_id: Optional[int] = None
        """:field
        A value to mark the overall "significance" of the collision event.
        """
        self.magnitude: float = 0
        """:field
        The velocity vector.
        """
        self.velocity: np.ndarray = np.array([0, 0, 0])
        if collision.state == "exit":
            return

        if isinstance(collision, CollisionObjObj):
            self.velocity = collision.relative_velocity
            self.magnitude = np.linalg.norm(self.velocity)
            valid_event = self.magnitude > 0.01
            obj_obj: bool = True
            if object_1_static is None:
                raise Exception("object_1_static is None but this is an object-object collision.")
        elif isinstance(collision, CollisionObjEnv):
            self.velocity = object_0_dynamic.velocity
            self.magnitude = np.linalg.norm(self.velocity)
            valid_event = self.magnitude > 0.01
            obj_obj = False
        else:
            raise Exception(f"Invalid collision type: {collision}")
        if not valid_event:
            return
        # Initially set this as an impact so we can find the previous area.
        self._set_as_impact(obj_obj=obj_obj, object_0_static=object_0_static, object_1_static=object_1_static)
        # Set the area.
        self.area = self._get_contact_area()
        # Get the previous area, if any.
        if self.primary_id in previous_areas:
            previous_area = previous_areas[self.primary_id]
        else:
            previous_area = None
        if self.collision.state == "stay":
            if previous_area is None:
                if self.area > CollisionAudioEvent.IMPACT_AREA_NEW_COLLISION:
                    self._set_as_impact(obj_obj=obj_obj,
                                        object_0_static=object_0_static,
                                        object_1_static=object_1_static)
                else:
                    self.collision_type = CollisionAudioType.none
            # This is a scrape or a roll.
            elif previous_area > 0 and self.area / previous_area < CollisionAudioEvent.IMPACT_AREA_RATIO:
                self._set_as_impact(obj_obj=obj_obj, object_0_static=object_0_static, object_1_static=object_1_static)
                # Get the angular velocity of the primary object.
                if obj_obj:
                    if object_1_dynamic is None:
                        raise Exception("object_1_dynamic is None but this is an object-object collision.")
                    # Set the primary and secondary bodies based on speed. Assume that the slower object is the surface.
                    if np.linalg.norm(object_0_dynamic.velocity) > np.linalg.norm(object_1_dynamic.velocity):
                        self.primary_id = object_0_static.object_id
                        self.secondary_id = object_1_static.object_id
                        angular_velocity = object_0_dynamic.angular_velocity
                    else:
                        self.primary_id = object_1_static.object_id
                        self.secondary_id = object_0_static.object_id
                        angular_velocity = object_1_dynamic.angular_velocity
                else:
                    angular_velocity = object_0_dynamic.angular_velocity
                # If the primary object has a high angular velocity, this is a roll.
                if np.linalg.norm(angular_velocity) > CollisionAudioEvent.ROLL_ANGULAR_VELOCITY:
                    # TODO set this to CollisionAudioType.roll once we have roll sounds.
                    self.collision_type = CollisionAudioType.impact
                # If the primary object has a low angular velocity, this is a scrape.
                else:
                    self.collision_type = CollisionAudioType.scrape
            else:
                self.collision_type = CollisionAudioType.none

    def _get_contact_area(self) -> float:
        """
        :return: The area of all of the contact points.
        """

        # Source: https://stackoverflow.com/a/68115011
        points = np.array(self.collision.points)
        edges = points[1:] - points[0:1]
        return sum(np.linalg.norm(np.cross(edges[:-1], edges[1:], axis=1), axis=1) / 2)

    def _set_as_impact(self, obj_obj: bool, object_0_static: ObjectAudioStatic, object_1_static: ObjectAudioStatic) -> None:
        """
        Set the primary (target) object and secondary (other) object for an impact event based on relative mass.

        :param obj_obj: If True, this is an object-object collision.
        :param object_0_static: Static data for the first object.
        :param object_1_static: Static data for the second object.
        """

        self.collision_type = CollisionAudioType.impact
        if not obj_obj:
            return
        elif object_0_static.mass < object_1_static.mass:
            self.primary_id = object_0_static.object_id
            self.secondary_id = object_1_static.object_id
        else:
            self.primary_id = object_1_static.object_id
            self.secondary_id = object_0_static.object_id
