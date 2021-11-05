##### Troubleshooting

# Good coding processes

There is no one "correct" way to program with TDW. This document explains some generally useful guidelines.

## 1. Extend the `Controller` class

Most of the tutorials in the TDW documentation look like this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies

"""
Drop an object and print its final position.
"""

c = Controller()

object_id = c.get_unique_id()
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object("iron_box",
                                       object_id=object_id,
                                       position={"x": 0, "y": 1.5, "z": 0}),
                      {"$type": "send_rigibodies",
                       "frequency": "always"},
                      {"$type": "send_transforms",
                       "frequency": "always"}])
sleeping = False
object_position = (0, 0, 0)
while not sleeping:
    for i in range(len(resp) - 1):
        r_id = OutputData.get_data_type_id(resp[i])
        if r_id == "tran":
            transforms = Transforms(resp[i])
            for j in range(transforms.get_num()):
                if transforms.get_id(j) == object_id:
                    object_position = transforms.get_position(j)
        elif r_id == "rigi":
            rigidbodies = Rigidbodies(resp[i])
            for j in range(rigidbodies.get_num()):
                if rigidbodies.get_id(j) == object_id:
                    sleeping = rigidbodies.get_sleeping(j)
    resp = c.communicate([])
print(object_position)
c.communicate({"$type": "terminate"})
```

That works fine for small examples, and is generally a very human-readable option. For large-scale projects, we recommend extending the `Controller` class with your own custom class.

In the above example, the object falls only once. We can reorganize  this code into "trials". In each trial, the object drops to the ground. Trials can be parameterized with different objects and starting heights, and we can return the output data from the trial to a list or dictionary:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies

class Drop(Controller):
    """
    Drop an object and print its final position.
    """
    
    def trial(self, model_name, height):
        """
        Drop an object from a given height.
        
        :param model_name: The name of the model.
        :param height: The starting height of the model.
        
        :return: The final position of the object.
        """
        
        object_id = self.get_unique_id()
        # Add an object. Request Rigidbodies and Transforms output data.
        resp = self.communicate([c.get_add_object(model_name,
                                                  object_id=object_id,
                                                  position={"x": 0, "y": height, "z": 0}),
                                 {"$type": "send_rigibodies",
                                  "frequency": "always"},
                                 {"$type": "send_transforms",
                                  "frequency": "always"}])
        # Call self.communicate() until the object is "sleeping" i.e. no longer moving.
        sleeping = False
        object_position = (0, 0, 0)
        while not sleeping:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse Transforms output data to get the object's position.
                if r_id == "tran":
                    transforms = Transforms(resp[i])
                    for j in range(transforms.get_num()):
                        if transforms.get_id(j) == object_id:
                            object_position = transforms.get_position(j)
                # Parse Rigidbody data to determine if the object is sleeping.
                elif r_id == "rigi":
                    rigidbodies = Rigidbodies(resp[i])
                    for j in range(rigidbodies.get_num()):
                        if rigidbodies.get_id(j) == object_id:
                            sleeping = rigidbodies.get_sleeping(j)
            resp = self.communicate([])
        # Destroy the object to reset the scene.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return object_position

    def run(self):
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))
        # Log the positions of the objects.
        positions = {}
        # Run a series of trials.
        for model_name, height in zip(["iron_box", "iron_box", "rh10"], [1.5, 13, 2.4]):
            position = self.trial(model_name=model_name, height=height)
            if model_name not in positions:
                positions[model_name] = []
            positions[model_name].append(position)
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Drop()
    c.run()
```

## 2. Reset the scene efficiently

This is covered more thoroughly [elsewhere](../objects_and_scenes/reset_scene.md) but you should manage objects and scenes carefully. In the above example, notice that we don't actually rebuild the scene at the start of each trial. For the sake of efficiency, we keep the same scene loaded and just destroy the object in the scene.

## 3. Compartmentalize your code

Generally, it's best to store values such as object IDs or object positions only in a single context (in this case, the `trial()` function). We *could*, if we wish, write code like this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies

class Drop(Controller):
    """
    Drop an object and print its final position.
    """
    
    def trial(self, model_name, height):
        self.object_id = c.get_unique_id()
```

But, because we don't need to reference `object_id` anywhere else, there is no reason to add the `self.` prefix. 

Compartmentalizing the scope of your code can prevent bugs. For example, another function could change the value of `self.object_id`, which can create bugs that are hard to trace. Compartmentalization can also be memory efficient because variables no longer in use are discarded.

Conversely, there are times when it's *far* more efficient to cache data than not. In the above example, if there was any data that never changes between trials, we'd want to store it as "static" data. Generally, "static" data that is needed for every trial or action should have the `self.` prefix and be instantiated in the constructor.

In this example, the same model is dropped per trial as opposed to different models. We'll store the model name as `self.model_name`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies


class Drop(Controller):
    """
    Drop an object and print its final position.
    """

    def __init__(self, model_name: str, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        # The name of the model.
        self.model_name = model_name

    def trial(self, height):
        """
        Drop an object from a given height.

        :param height: The starting height of the model.

        :return: The final position of the object.
        """

        object_id = self.get_unique_id()
        # Add an object. Request Rigidbodies and Transforms output data.
        resp = self.communicate([c.get_add_object(self.model_name,
                                                  object_id=object_id,
                                                  position={"x": 0, "y": height, "z": 0}),
                                 {"$type": "send_rigibodies",
                                  "frequency": "always"},
                                 {"$type": "send_transforms",
                                  "frequency": "always"}])
        # Call self.communicate() until the object is "sleeping" i.e. no longer moving.
        sleeping = False
        object_position = (0, 0, 0)
        while not sleeping:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse Transforms output data to get the object's position.
                if r_id == "tran":
                    transforms = Transforms(resp[i])
                    for j in range(transforms.get_num()):
                        if transforms.get_id(j) == object_id:
                            object_position = transforms.get_position(j)
                # Parse Rigidbody data to determine if the object is sleeping.
                elif r_id == "rigi":
                    rigidbodies = Rigidbodies(resp[i])
                    for j in range(rigidbodies.get_num()):
                        if rigidbodies.get_id(j) == object_id:
                            sleeping = rigidbodies.get_sleeping(j)
            resp = self.communicate([])
        # Destroy the object to reset the scene.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return object_position

    def run(self):
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))
        # Log the positions of the objects.
        positions = []
        # Run a series of trials.
        for height in [1.5, 13, 2, 4.5, 5.1]:
            position = self.trial(height=height)
            positions.append(position)
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Drop(model_name="iron_box")
    c.run()
```

## 4. Load data from .json files

For more complex seasons, it can be inefficient to store data within a controller. In this cases, we find it useful to load data from a saved .json file.

In this example, we'll load trial data from a `trials.json` file:

```json
{"trials": [
  {"model_name": "iron_box", "height":  1.5},
  {"model_name": "iron_box", "height":  13},
  {"model_name": "rh10", "height":  2.4},
]}
```

And then we'll load the trial data in the `run()` function:

```python
import json
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies


class Drop(Controller):
    """
    Drop an object and print its final position.
    """

    def trial(self, model_name, height):
        """
        Drop an object from a given height.

        :param model_name: The name of the model.
        :param height: The starting height of the model.

        :return: The final position of the object.
        """

        object_id = self.get_unique_id()
        # Add an object. Request Rigidbodies and Transforms output data.
        resp = self.communicate([c.get_add_object(model_name,
                                                  object_id=object_id,
                                                  position={"x": 0, "y": height, "z": 0}),
                                 {"$type": "send_rigibodies",
                                  "frequency": "always"},
                                 {"$type": "send_transforms",
                                  "frequency": "always"}])
        # Call self.communicate() until the object is "sleeping" i.e. no longer moving.
        sleeping = False
        object_position = (0, 0, 0)
        while not sleeping:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse Transforms output data to get the object's position.
                if r_id == "tran":
                    transforms = Transforms(resp[i])
                    for j in range(transforms.get_num()):
                        if transforms.get_id(j) == object_id:
                            object_position = transforms.get_position(j)
                # Parse Rigidbody data to determine if the object is sleeping.
                elif r_id == "rigi":
                    rigidbodies = Rigidbodies(resp[i])
                    for j in range(rigidbodies.get_num()):
                        if rigidbodies.get_id(j) == object_id:
                            sleeping = rigidbodies.get_sleeping(j)
            resp = self.communicate([])
        # Destroy the object to reset the scene.
        self.communicate({"$type": "destroy_object",
                          "id": object_id})
        return object_position

    def run(self):
        # Load the trial data.
        trial_data = json.loads("trials.json")
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))
        # Log the positions of the objects.
        positions = {}
        # Run a series of trials.
        for trial in trial_data:
            model_name = trial["model_name"]
            height = trial["height"]
            position = self.trial(model_name=model_name, height=height)
            if model_name not in positions:
                positions[model_name] = []
            positions[model_name].append(position)
        # End the simulation.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    c = Drop()
    c.run()
```

***

**Next: [The `Logger` add-on](logger.md)**

[Return to the README](../../../README.md)

