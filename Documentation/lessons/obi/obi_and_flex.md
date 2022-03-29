##### Physics (Obi)

# Obi and Flex

[Flex](../flex/flex.md) is a particle-based physics engine that is in many ways similar to Obi. Flex was added to TDW long before Obi. Obi is intended as a replacement to Flex. **In nearly all use-cases, we recommend using Obi instead of Flex.** 

There are two reasons to use Flex instead of Obi:

- If you have an ongoing project that uses Flex.
- If you want to add softbodies or cloth, both of which Obi supports but haven't yet been added to TDW.

## Platform Compatibility

Obi has far more cross-platform support than Flex:

|                      | Obi  | Flex |
| -------------------- | ---- | ---- |
| Softbodies - Windows | Yes* | Yes  |
| Softbodies - OS X    | Yes* | No   |
| Softbodies - Linux   | Yes* | Yes  |
| Cloth - Windows      | Yes* | Yes  |
| Cloth - OS X         | Yes* | No   |
| Cloth - Linux        | Yes* | Yes  |
| Fluids - Windows     | Yes  | Yes  |
| Fluids - OS X        | Yes  | No   |
| Fluids - Linux       | Yes  | No   |

\* Obi cloth and soft-bodies haven't yet been implemented in TDW. However, when they *are* implemented, they will be compatible with Windows, OS X, and Linux.

## Model Compatibility

Only a subset of TDW's models are compatible in Flex.

All of TDW's models are compatible in Obi.

## Stability

Flex has many known issues and is no longer actively supported by its developers.

Obi is very stable and actively supported by its developers.

## Ease of use

Many TDW users have noted that Flex is difficult to set up correctly such that it doesn't crash and doesn't have buggy or unrealistic behavior.

Obi tends to work much better than Flex when using default values for parameters.

## Output data

[Flex particle data](../flex/output_data.md) is very similar to [Obi particle data](obi_particles.md) but there are two key differences that make Obi particle data easier to use overall:

1. [It isn't possible to receive Flex particle data in a fluid simulation.](../flex/fluid_and_source.md) Obi supports particle output data for *all* types of actors, including fluids.
2. The build is capable of marshalling, serializing, and sending Obi particle data and a much faster rate than Flex particle data.

## Speed

Obi's main disadvantage compared to Flex is its speed; Flex is much faster.

[This controller](https://github.com/threedworld-mit/tdw/blob/master/Python/benchmarking/obi_fluid.py) benchmarks Obi when a single [fluid emitter](fluids.md) is added to the scene. There are two trials, one with output data and one without.

[This controller](https://github.com/threedworld-mit/tdw/blob/master/Python/benchmarking/flex_fluid.py) benchmarks Flex when a single [fluid source](../flex/fluid_and_source.md) is added to the scene.

In both of these trials, the volume of fluid is the same (1 cubic meter).

| Obi (without output data) | Obi (with output data) | Flex |
| ------------------------- | ---------------------- | ---- |
| 60                        | 54                     | 109  |

A few things worth noting about these benchmarks:

- Obi particle data barely impacts overall simulation speed.
- It isn't possible to benchmark Flex fluids with particle output data.
- Right now, only Obi fluids have been implemented in TDW and this benchmark is therefore to some extent inconclusive. As we add more Obi features to TDW, we will add more benchmark data.

***

**This is the last document in the "Obi" tutorial.**

[Return to the README](../../../README.md)

***