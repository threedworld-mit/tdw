# Command API

**Commands** are instructions that are sent by the controller to the build per frame.

In a controller, a command is a dictionary like this:

```python
{"$type": "set_screen_size", "width": 1024, "height": 1024}
```

Where the value of `"$type"`  defines the  type of command (in this case, `"set_screen_size"`).

To send this command, you must call the controller's `communicate(commands)` function:

```python
from tdw.controller import Controller

c = Controller() 
c.communicate({"$type": "set_screen_size", "width": 1024, "height": 1024})
c.communicate({"$type": "terminate"})
```

## Simulation frames

Every time you call `c.communicate(commands)`, the build does the following:

1. Receives the commands
2. Executes the commands in order from the first command in the list of `commands` to the last
3. Advances one simulation frame
4. Send output data to the controller

The build doesn't advance between `c.communicate(commands)` calls; it pauses until it receives the next list of commands.

A simulation frame is usually equal to a physics frame, or a physics time step. However, there is one command, `step_physics`, that can advance the simulation multiple physics frames per simulation step. It is usually included in a controller in order to speed up the simulation:

```python
from tdw.controller import Controller

c = Controller() 
c.communicate({"$type": "step_physics", "frames": 10})
c.communicate({"$type": "terminate"})
```

## Sending list of commands

You can send arbitrarily long lists of commands  to the build on the same simulation step. These commands will execute in order from the first command in the list to the last. This allows for highly complex behavior in TDW such as adding multiple objects at the same time or moving multiple robot joints on the same frame:

```python
from tdw.controller import Controller

c = Controller()
# On the same frame, load a scene, set the screen size, and advance 10 physics steps.
c.communicate([{"$type": "load_scene",
               "scene_name": "ProcGenScene"},
               {"$type": "set_screen_size",
                "width": 1024,
                "height": 1024},
               {"$type": "step_physics",
                "frames": 10}])
c.communicate({"$type": "terminate"})
```

## Parameters with default values

Many commands have parameters with default values. In these cases, it isn't necessary to include the parameter in the dictionary.

 For example: `{"$type": "create_avatar", "type": "A_Img_Caps"}` is equivalent to `{"$type": "create_avatar", "type": "A_Img_Caps", "id": "a"}` because the default parameter of `"id"` is `"a"`. 

To learn which parameters have default values, read the [Command API documentation](../api/command_api.md).

## Command API Documentation

For complete documentation of the Command API, [read this](../api/command_api.md).

## If you need more commands...

...don't hesitate to reach out to us via email or Slack! The Command API is designed to be easily improved and extended and we'll usually be able to add the functionality you need.

***

Next: 

- [Scenes](scenes.md)
- [Command API documentation](../api/command_api.md)

[Return to the README](../../README.md)
