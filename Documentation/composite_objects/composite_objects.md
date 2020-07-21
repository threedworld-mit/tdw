# Composite Objects

Composite Objects are any models that have _sub-objects_ that can be referenced to in the TDW API.

Each sub-object may also be a _mechanism_ (a TDW-specific idiom). Currently, the following mechanism have been implemented:

| Mechanism | Behavior                                                     | Example                |
| --------- | ------------------------------------------------------------ | ---------------------- |
| `hinge`   | Swings freely on a pivot point around an axis.               | A box with a lid       |
| `motor`   | Can rotate on a pivot point around an axis by applying a target velocity and a force magnitude. | A helicopter propeller |
| `spring`  | Can rotate on a pivot point around an axis by applying a target position. The motion will appear "spring-like" | Jack-in-the-box        |
| `light`   | Can be turned on or off.                                     | A lightbulb            |
| `none`    | (No mechanism)                                               | A chest of drawers     |

### Output Data

Each sub-object has a Rigidbody, segmentation color, etc. All of this can be retrieved from output data like any other object (e.g. via `send_transforms` or `send_rigidbodies`). The difference is that each sub-objects ID is defined by Unity at runtime rather than assigned by the user in a controller.

To receive a map of sub-objects in a composite object, send the [`send_composite_objects`](../api/command_api#send_composite_objects) command to receive [`CompositeObjects`](../api/output_data.md#CompositeObjects) data.

### Command API

Certain commands can only be sent to certain types of sub-objects (e.g. `set_motor` only works with motors). For a list of all sub-object commands, see the [Command API documentation](../api/command_api.md) under "SubObjectCommand".

### Example Controllers

There are two [example controllers](../python/example_controllers.md) for composite objects:

- `composite_object.py` (Tests output data and sub-object commands)
- `open_box.py` (Basic demo of a Sticky Mitten Avatar opening a box with a lid)

### Creating Composite Objects

Read [Creating Composite Objects](creating_composite_objects.md).