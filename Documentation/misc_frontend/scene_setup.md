# Scene Setup

The following are useful tips for "staging" a scene in TDW (adding objects, adding avatars, etc.) They are not meant to be the final word on how to stage a scene; some techniques will work better for your particular use-case than others.

### Compartmentalize your code

This is a technique often used in game design. If you compartmentalize the code required to initialize the scene from the rest of the simulation, you can iterate on refining the initialization without having to run anything else.

```python
class YourController(Controller):
	def initialize(self):
		# Your code here

	def do_trial(self):
		# Your code here

c = YourController()

# I only want to test initialization, so I'll just call initialize() for now...
c.initialize()
# c.do_trial()s
```

### Use the keyboard to position objects

You can position objects in the scene by using the arrow keys. See `example_controllers/keyboard.py` for an example of keyboard input. To record the final positions and rotations of the objects, you can send `send_transforms`.

```python
from getch import getch
from tdw.output_data import Transforms

# Code to initialize the controller and scene goes here.

o_id = c.add_object("iron_box")

c.communicate({"$type": "send_transforms",
			   "frequency": "always"})

char = getch()

if char == b'w':
	resp = c.communicate({"$type": "teleport_object",
						  "position": {"x": 1, "y": 0, "z": 0}, 
						  "id": o_id})
	transform = Transforms(resp[0])
    
    # Get the position and rotation of the iron_box object.
	position = transform.get_position(0)
	rotation = transform.get_rotation(0)
```

### Use the `simulate_physics` command

Often, objects will move from the time you add them to the scene to the time when you've fully initialized the scene. This is because every list of commands you send to the build steps forward one physics frame. (For more information on how physics frames work, see the [Command API Guide](../api/command_api_guide.md)). 

Send `simulate_physics` to disable physics stepping. The physics engine won't respond to any new objects, forces, etc. until you manually re-enable it.

```python
c.communicate({"$type": "simulate_physics",
			   "value": False})

# Code to add objects goes here.

# Re-enable physics.
c.communicate({"$type": "simulate_physics",
			   "value": True})
```
