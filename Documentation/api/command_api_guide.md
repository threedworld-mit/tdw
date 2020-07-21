# How to Use Commands

The [Command API](command_api.md) is used to send commands from the controller to the build (via the server). Each command is a JSON object that has matching code in the build. The build will deserialize each command and then execute the associated process. For example, if you want to disable physics, the command is:

```python
{"$type": "simulate_physics", "value": False}
```

## Order of Execution

1. The build receives a list of commands.
2. The build executes each command in the list sequentially. Each new command will only begin after the previous command ends.
3. The build advances 1 physics frame.
4. The build sends output data.

## Initialization

To initialize TDW, you always need to load a _scene_ followed by an _environment_. See the [Getting Started guide](../getting_started.md) for more information.

### Bad Example A

```python
communicate([add_object, load_scene, create_exterior_walls, create_avatar])
```

In this example, the build executes `add_object` first but there is no scene or environment in which to add the object. The build crashes.

### Bad Example B

```python
communicate([create_exterior_walls, load_scene, add_object, create_avatar])
```

The build tries to create the proc-gen room, but the scene hasn't been loaded yet. The build crashes.

### Good Example C

```python
communicate([load_scene, create_exterior_walls, add_object, create_avatar])
```

The build loads the scene, then generates the room, and then adds an object and an avatar. 

### Mediocre Example D

```python
communicate([load_scene])
communicate([create_exterior_walls])
communicate([add_object])
communicate([create_avatar])
```

This isn't a *wrong* way to use TDW but often not the best way. In this example, you've spread out your commands across 4 simulation steps. If, for example, `add_object` places the object in midair, by the time `create_avatar` is sent, the object will already be falling.

When sending only one command, it doesn't need to be in a list; `communicate(create_avatar)` and `communicate([create_avatar])` both work.

### Good Example E

```python
resp = communicate([load_scene, create_exterior_walls, add_object, create_avatar, send_bounds])

commands = interpret_response(resp) # You need to define this.

communicate(commands)
```

This is an example of when you *will* need to divided your commands into multiple lists. 

You receive [`Bounds` output data](output_data.md) and advance one simulation step. You then interpret that data (using a function that you wrote) to decide what commands to send next. Then, you send those commands.

## Parameters with Default Values

Many commands have parameters with **default values**. If you don't include these parameters in your JSON command, they will default to a value.

For example, in the command `create_avatar`, the default value of `"id"` is `"a"`.

| This...                                            | ...is the same as this.                                      |
| -------------------------------------------------- | ------------------------------------------------------------ |
| `{"$type": "create_avatar", "type": "A_Img_Caps"}` | `{"$type": "create_avatar", "type": "A_Img_Caps", "id": "a"}` |

Every command in the [Command API](command_api.md) includes an example of a JSON dictionary with, and without, parameters with default values, along with a parameter table that includes the default values.

## Example Controllers

We've included many example implementations of the [Command API](command_api.md) as example controllers. Read [this document](../python/example_controllers.md) for a list of all example controllers.

## Requesting New Commands

The  [Command API](command_api.md) is very easy to improve and extend. If there is a command that you'd like that is not currently in the API, just let us know. 
