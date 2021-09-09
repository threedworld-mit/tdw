##### Core Concepts

# Commands

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

## Sending list of commands

You can send arbitrarily long lists of commands  to the build on the same simulation step. These commands will execute in order from the first command in the list to the last. This allows for highly complex behavior in TDW such as adding multiple objects at the same time or moving multiple robot joints on the same frame:

```python
from tdw.controller import Controller

c = Controller()
# On the same frame, set the screen size and disable physics.
c.communicate([{"$type": "set_screen_size",
                "width": 1024,
                "height": 1024},
               {"$type": "simulate_physics",
                "value": False}])
c.communicate({"$type": "terminate"})
```

## Parameters with default values

Many commands have parameters with default values. In these cases, it isn't necessary to include the parameter in the dictionary.

 For example:

 `{"$type": "create_avatar", "type": "A_Img_Caps"}` 

...is equivalent to

 `{"$type": "create_avatar", "type": "A_Img_Caps", "id": "a"}` 

...because the default parameter of `"id"` is `"a"`. 

To learn which parameters have default values, read the [Command API documentation](../../api/command_api.md).

## API

TDW includes hundreds of commands. **[Read the Command API documentation here.](../../api/command_api.md)**

## If you need more commands...

...don't hesitate to reach out by posting a GitHub issue! The Command API is designed to be easily improved and extended and we'll usually be able to add the functionality you need.

***

See also: 

- [Command API](../../api/command_api.md)

***

**Next: [Design philosophy of TDW](design_philosophy.md)**

[Return to the README](../../../README.md)
