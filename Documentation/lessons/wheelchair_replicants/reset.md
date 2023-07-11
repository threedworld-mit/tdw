##### Wheelchair Replicants

# Reset

Call `replicant.reset()` to reset a Wheelchair Replicant when you start a new scene. This will destroy the current Wheelchair Replicant and reset the add-on's state (e.g. static and dynamic data, collision detection rules, etc.). To properly reset a Wheelchair Replicant, you must also destroy and recreate the scene; otherwise, a copy of this Wheelchair Replicant will be created without destroying the current one.

In this controller, we'll run several "trials" and reset the scene each time. To end the scene, we'll clear the add-ons to prevent them from resetting and then send `{"$type": "terminate"}`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.wheelchair_replicant import WheelchairReplicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.replicant.action_status import ActionStatus
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class Reset(Controller):
    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.replicant = WheelchairReplicant()
        self.camera = ThirdPersonCamera(position={"x": 2, "y": 3, "z": 2.53},
                                        look_at=self.replicant.replicant_id,
                                        avatar_id="a")
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("wheelchair_replicant_reset")
        print(f"Images will be saved to: {path}")
        self.capture = ImageCapture(avatar_ids=[self.camera.avatar_id], path=path)
        self.add_ons.extend([self.replicant, self.camera, self.capture])

    def trial(self, distance: float):
        # Load a new scene.
        self.communicate([{"$type": "load_scene",
                           "scene_name": "ProcGenScene"},
                          TDWUtils.create_empty_room(12, 12)])
        self.replicant.move_by(distance=distance)
        while self.replicant.action.status == ActionStatus.ongoing:
            self.communicate([])
        self.communicate([])
        # End the trial by resetting the add-ons.
        self.replicant.reset()
        self.camera.initialized = False
        # Remember the current frame count.
        f = self.capture.frame
        # Reset image capture.
        self.capture.initialized = False
        # Set the current frame count.
        self.capture.frame = f

    def end(self) -> None:
        # Clear the add-ons so that nothing tries to initialize when we terminate.
        self.add_ons.clear()
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Reset()
    for d in [1, 2, 3]:
        c.trial(distance=d)
    c.end()
```

Result:

![](images/reset/reset.gif)

You can optionally set the `position` and `rotation` parameters of `reset()`:

```
        self.replicant.reset(position={"x": 0, "y": 0, "z": 0},
                             rotation={"x": 0, "y": 0, "z": 0})
```

***

**This is the last document in the "Wheelchair Replicants" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [reset.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/wheelchair_replicant/reset.py) Run a series of trials and reset the scene each time.

Python API:

- [`WheelchairReplicant`](../../python/add_ons/wheelchair_replicant.md)