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

[Flex particle data](../flex/output_data.md) is very similar to [Obi particle data](obi_particles.md). The main difference is that [it isn't possible to receive Flex particle data in a fluid simulation.](../flex/fluid_and_source.md) Obi supports particle output data for *all* types of actors, including fluids.

## Speed

Obi's main disadvantage compared to Flex is its speed. Flex cloth is somewhat more performant than Obi cloth. Flex fluids are much more performant than Obi fluids.

### Cloth

[This controller](https://github.com/threedworld-mit/tdw/blob/master/Python/benchmarking/obi_vs_flex/obi_cloth.py) benchmarks Obi cloth. There are two trials, one with output data and one without.

[This controller](https://github.com/threedworld-mit/tdw/blob/master/Python/benchmarking/obi_vs_flex/flex_cloth.py) benchmarks Flex cloth. There are two trials, one with output data and one without.

|                    | Obi  | Flex |
| ------------------ | ---- | ---- |
| **Particle count** | 3721 | 4225 |

| Obi (without output data) | Obi (with output data) | Flex (without output data) | Flex (with output data) |
| ------------------------- | ---------------------- | -------------------------- | ----------------------- |
| 47                        | 45                     | 68                         | 61                      |

### Fluids 

[This controller](https://github.com/threedworld-mit/tdw/blob/master/Python/benchmarking/obi_vs_flex/obi_fluid.py) benchmarks Obi when a single [fluid emitter](fluids.md) is added to the scene. There are two trials, one with output data and one without.

[This controller](https://github.com/threedworld-mit/tdw/blob/master/Python/benchmarking/obi_vs_flex/flex_fluid.py) benchmarks Flex when a single [fluid source](../flex/fluid_and_source.md) is added to the scene. It isn't possible to benchmark Flex fluids with particle output data.

In both of these trials, the volume of fluid is the same (1 cubic meter).

| Obi (without output data) | Obi (with output data) | Flex |
| ------------------------- | ---------------------- | ---- |
| 60                        | 54                     | 109  |

***

**This is the last document in the "Obi" tutorial.**

[Return to the README](../../../README.md)

***