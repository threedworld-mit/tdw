# Virtual Reality

## Setup

This document assumes that you have the required VR hardware and have set up VR support on your machine. Generally, you want to have a GPU that can run at 90 FPS or more on a VR headset.

**TDW supports Oculus VR with Touch controls.**

### Creating a VR Rig

You can enable virtual reality (VR) in TDW by sending the [command](../api/command_api.md) `create_vr_rig`.

VR rig movement (head, hands, etc.) is _not_ constrained by TDW's strict [frame-stepping pattern](../api/command_api_guide.md); you will be able to look around and move your hands without sending any commands after `create_vr_rig`. However, in order for the build to simulate physics and send output data, more commands must be sent.

#### Mediocre Example A

```python
# Create the VR rig.
c.communicate({"type": "create_vr_rig"})
```

In this example, the control won't receive any output data, and the build won't simulate physics.

#### Good Example B

```python
# Create the VR rig.
c.communicate({"type": "create_vr_rig"})

while True:
    # Receive output data.
    resp = c.communicate({"$type": "do_nothing"})
```

## Other Commands

For a full description of VR commands, refer to the [Command API documentation](../api/command_api.md).

| Command                   | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `teleport_vr_rig`         | Set the position of the VR rig.                              |
| `set_graspable`           | Set an object as "graspable" by the VR rig.                  |
| `destroy_vr_rig`          | Destroy the VR rig.                                          |
| `send_vr_data`            | Send [VR Data](../api/output_data.md).                       |
| `attach_avatar_to_vr_rig` | Attach an avatar to the VR rig. This will allow the VR rig to return the same output data as an avatar (Images, IdPassSegmentationColors, etc.) By default, this feature is disabled because it slows down the simulation's FPS. |

## Examples

There are several VR example controllers. See [Example Controllers](../python/example_controllers.md).

## Running TDW without VR hardware

You can run non-VR TDW simulations on machines that don't have the required hardware or libraries. See [Debug TDW](debug_tdw.md) for more information.

## VR and Avatars

A VR rig is not, strictly speaking, an avatar, and won't respond to avatar commands, send images, etc. However, by sending the command `attach_avatar_to_vr_rig`, you can "attach" an avatar to the head of the VR rig; this avatar behaves like any other avatar, except that its camera will match the motion of the VR headset.

There is a tradeoff: Because the VR headset renders at a high resolution, the framerate can drop significantly when receiving `Images` or `IdPassSegmentationColors`. See [performance optimizations](../benchmark/performance_optimizations.md) for more information.

## Known Limitations

- TDW's VR support is a large and new feature, and as such might not be as stable as other supported features. If you find your simulation to be buggy, please let Seth or Jeremy know.
- When using VR with [Flex](flex.md), the particles of a "held" object will have no velocity (0, 0, 0).

## Roadmap

In addition to continuously providing more stable support of existing VR hardware, we will in the future add support for the Oculus + Leap Motion, and the HTC Vive.