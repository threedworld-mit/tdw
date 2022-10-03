##### Semantic States

# Open and closed states

*Open and closed states involve composite objects. If you haven't done so already, [read the documentation for composite objects.](../composite_objects/overview.md)*

For **hinges, motors, and springs** it is possible to determine whether an object is "open" by defining an angle threshold; if the current angle is above the threshold, then the object is "open":

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.composite_object_manager import CompositeObjectManager


class CompositeObjectOpen(Controller):
    """
    Determine when a composite object is "open".
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self.composite_object_manager = CompositeObjectManager()
        self.add_ons.append(self.composite_object_manager)

    def trial(self, open_at: float):
        # Reset the composite object manager.
        self.composite_object_manager.reset()
        # Add the object.
        object_id = Controller.get_unique_id()
        self.communicate(Controller.get_add_physics_object(model_name="b03_bosch_cbg675bs1b_2013__vray_composite",
                                                           object_id=object_id,
                                                           kinematic=True))
        # Get the hinge ID.
        hinge_id = list(self.composite_object_manager.static[object_id].hinges.keys())[0]
        # Apply a torque to the hinge.
        self.communicate({"$type": "apply_torque_to_object",
                          "id": hinge_id,
                          "torque": {"x": 0.5, "y": 0, "z": 0}})
        for i in range(200):
            # Get the angle of the hinge.
            angle = self.composite_object_manager.dynamic[object_id].hinges[hinge_id].angle
            # Check if the hinge is open.
            is_open = angle >= open_at
            if is_open:
                print(f"Microwave door is open on frame {i} at angle {angle}.")
                break
            self.communicate([])
        # Destroy the object.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})


if __name__ == "__main__":
    c = CompositeObjectOpen()
    c.trial(open_at=30)
    c.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = CompositeObjectOpen()
    c.trial(open_at=30)
    c.communicate({"$type": "terminate"})
```

Output:

```
Microwave door is open on frame 16 at angle 30.119487762451172.
```

***

**Next: [Grasped objects](grasped.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [composite_object_open.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/semantic_states/composite_object_open.py) Determine when a composite object is "open".

Python API:

- [`CompositeObjectManager`](../../python/add_ons/composite_object_manager.md)