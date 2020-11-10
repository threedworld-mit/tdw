# TDW Physics

This document includes common questions or problems users have encountered when creating physics simulations in TDW.

### "Objects are passing through each other, physics is non-deterministic, physics feels 'floaty', etc."

These [commands](../api/command_api.md) can improve the overall physics quality of your simulation:

| Command                         | Effect                                                       |
| ------------------------------- | ------------------------------------------------------------ |
| `set_physics_solver_iterations` | Set the number of physics solver iterations, which affects the overall accuracy of the physics engine. |
| `set_time_step`                 | Set the physics time step per frame. The actual affect though isn't totally intuitive; see [documentation](../api/command_api.md#set_time_step). |

See [Physics Determinism](../benchmark/determinism.md) for a benchmark.

### "Objects are not behaving realistically."

Try these commands:

| Command                                               | Effect                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------ |
| `set_mass`                                            | Set the mass of the object; many models may initially have a lower mass than you might expect. |
| `set_avatar_mass`                                     | Set the mass of an avatar.                                   |
| `set_physic_material`                                 | Assign friction and "bounciness" values to an object.        |
| `set_avatar_physic_material`                          | Assign friction and "bounciness" values to an avatar.        |
| `set_semantic_material`<br>`set_semantic_material_to` | Assign friction and "bounciness" values by material type.    |

### "I want to stop an object."

Send the `set_avatar_drag` or `set_object_drag` command. See [avatar movement documentation](avatar_movement.md) (the section about avatar drag applies to objects as well; just send `set_object_drag` instead).

### "I want to simulate multiple physics frames per step."

Send the `step_physics` command.

### "I want to use soft-bodies, cloth, fluids, etc."

See [NVIDIA Flex documentation](flex.md).

### "I want to disable physics."

Try these commands:

| Command                      | Effect                                                       |
| ---------------------------- | ------------------------------------------------------------ |
| `simulate_physics`           | If `"value" == False`, TDW will continue to advance frames, but won't simulate physics. |
| `set_avatar_kinematic_state` | Set an avatar's Rigidbody to be kinematic or not. A kinematic object won't respond to PhysX physics. |
| `set_kinematic_state`        | Set an object's Rigidbody to be kinematic or not. A kinematic object won't respond to PhysX physics. |

### "I want to include audio in my physics simulation."

See [impact sounds documentation](impact_sounds.md).

### "I want to receive physics metadata."

This [output data](../api/output_data.md) may be useful:

| Output Data   | Command            | Contents                                |
| ------------- | ------------------ | --------------------------------------- |
| `Transforms`  | `send_transforms`  | Positions, rotations, etc.              |
| `Rigidbodies` | `send_rigidbodies` | Velocities, masses, etc.                |
| `Collision`   | `send_collisions`  | Relative velocity, contact points, etc. |

Additionally, see the [TDW Physics repo](https://github.com/alters-mit/tdw_physics) for a useful set of controllers for generating physics datasets.