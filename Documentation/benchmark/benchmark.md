# Benchmarks

#### TDW v1.5.0

## Overview

**These benchmarks test the speed of TDW.**

### What do we mean by "speed?"

We measure speed by **FPS** (frames per second). FPS is  _the time elapsed between the controller sending a message and receiving a multipart message from the build._ The FPS can vary depending on the size of the data object, and the process required to generate the data.

### What affects speed?

Because TDW is a general-purpose tool, there are [innumerable optimizations](performance_optimizations.md) you can make. That said, there are four _innate and unavoidable_ causes of potential slowdown: 

#### 1. The machine

The faster the machine (and, especially, the faster the GPU), the faster TDW will run.

We benchmark on 3 machines:

| Machine                 | OS                   |
| ----------------------- | -------------------- |
| `legion_lenovo_windows` | Windows 10           |
| `legion_lenovo_ubuntu`  | Ubuntu 18            |
| `braintree`             | Ubuntu 16 (headless) |
| `node11`                | Ubuntu 16 (headless) |

- [Machine Performance](machine_performance.md)

#### 2. Command deserialization

[Commands](../api/command_api_guide.md) are sent as JSON strings which are deserialized into objects. The quantity of commands sent per frame will affect the speed of the build.

- [Command deserialization benchmarks](command_deserialization.md)

#### 3. Image capture

**Image capture is the slowest process in TDW.** Unfortunately, the code required to capture an image is part of the Unity Engine and can't be edited.

- [Image capture benchmarks](image_capture.md)
- [Observation data alternatives](observation_data.md)

#### 4. The main Unity loop

The main Unity loop has an innate and unavoidable slowness. We need to use this loop in order to call any Unity Engine-related functions (e.g. image capture).

- [Unity Engine benchmarks](unity_loop.md)

## What _doesn't_ affect speed?

- [Outputting general object data](object_data.md)
- [The network socket code library (ZMQ)](unity_loop.md) 

## Benchmarks

### 0. Object data

- `Transforms` data is sent per frame.
- The render quality is set to the highest possible setting (but no images are sent).
- There are 100 cube primitives in the scene.

| Machine       | FPS                |
| ------------- | ------------------ |
| legion_lenovo_windows |  590 |
| legion_lenovo_ubuntu | 850 |
| braintree     | 600 |
| node11        |  |

### 1. Image capture (low quality)

- `Images` data is sent per frame (`_img` pass only).
- The render quality is set to the lowest possible setting.
- The images are compressed .jpg
- The images are 256x256.
- There are no objects in the scene.

| Machine               | FPS                            |
| --------------------- | ------------------------------ |
| legion_lenovo_windows | 300 |
| legion_lenovo_ubuntu  | 386  |
| braintree             | 165           |
| node11                | 229              |

### 2. Image capture (high quality)

- `Images` data is sent per frame (`_img` pass only).
- The render quality is set to the highest possible setting.
- The images are compressed .jpg
- The images are 1024x1024.
- There are no objects in the scene.

| Machine       | FPS                    |
| ------------- | ---------------------- |
| legion_lenovo_windows | 43 |
| legion_lenovo_ubuntu | 38 |
| braintree     | 25 |
| node11        | 25    |

### 3. "Real World" benchmark

`real_world_benchmarker.py` moves the avatar per frame. Because there are less objects in the scene, the real-world benchmark might be faster than the "ideal" benchmark (which generates 100 boxes). Because of the random movements, the real-world benchmark is not deterministic (reported speeds will vary).

- `Images` data is sent per frame (`_img` pass only).
- The render quality is set to the lowest possible setting.
- The images are compressed .jpg
- The images are 256x256
- There are objects in the scene, sending the following [data](../api/output_data.md):
	- `Transforms`
	- `Rigidbodies`
	- `Collisions`
- [`IdColors`](observation_data.md) is sent per frame.

| Machine               | FPS                               |
| --------------------- | --------------------------------- |
| legion_lenovo_windows | 131 |
| legion_lenovo_ubuntu  | 168  |
| braintree             |              |
| node11                |                 |

### 4. Flex benchmark

`flex_benchmarker.py` runs a basic Flex simulation. The build sends `FlexParticles`, `Transforms`, `CameraMatrices`, and `Collisions`.

| Machine               | FPS                               |
| --------------------- | --------------------------------- |
| legion_lenovo_windows | 204 |
| braintree             |              |
| node11                |                 |

## How to update these benchmarks

### Update this document

#### Setup

1. **Make sure you are using the latest build and the latest Python scripts.**
2. Begin a new benchmark:

```bash
cd <root>/Python/benchmarking
python3 begin_benchmark.py <TDW version>
```

You only need to run this on one machine.

3. You need to perform all of the following steps on each of these machines:
	1. `legion_lenovo` (Windows)
	2. `legion_lenovo` (Ubuntu)
	3. `braintree`
	4. `node11`

To update this document across multiple machines, use git and push each update.

#### Run the benchmarks

1. Run the image capture benchmarks:

```bash
cd <root>/Python/benchmarking
python3 image_capture.py --main --machine <machine name>
```

```bash
<run build>
```

2. Run the real world benchmark:

```bash
cd <root>/Python/benchmarking
python3 real_world_benchmark.py --main --machine <machine name>
```

```bash
<run build>
```

4. Run the following benchmarks (all benchmarking scripts are in `<root>/Python/benchmarking`):
	- [Command Deserialization](command_deserialization.md)
	- [Image Capture](image_capture.md)
	- [Object Data](object_data.md)
	- [Observation Data](observation_data.md)
	- [Machine Performance](machine_performance.md)
	- [Unity Performance](unity_loop.md)
    - [Physics Determinism](determinism.md)
	
5. Run the Flex benchmark:

```bash
cd <root>/Python/benchmarking
python3 flex_benchmarker.py --main --machine <machine name>
```

```bash
<run build>
```