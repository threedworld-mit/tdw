##### Performance Benchmarks

# Performance Benchmarks

**These benchmarks test the FPS (frames per second) of TDW.** FPS is  _the time elapsed between the controller sending a message and receiving a multipart message from the build._ The FPS can vary depending on the size of the data object, and the process required to generate the data.

## Test machine system info

| OS      | CPU             | Memory | GPU                     | Python | TDW   |
| ------- | --------------- | ------ | ----------------------- | ------ | ----- |
| Windows | 4.2 Ghz 8 Cores | 17 GB  | NVIDIA GeForce GTX 1080 | 3.7.5  | 1.9.0 |

## Performance Benchmarks

### 0. Object data

- `Transforms` data is sent per frame.
- The render quality is set to the highest possible setting (but no images are sent).
- There are 100 cube primitives in the scene.

**FPS: 681**

### 1. Image capture (low quality)

- `Images` data is sent per frame (`_img` pass only).
- The render quality is set to the lowest possible setting.
- The images are compressed .jpg
- The images are 256x256.
- There are no objects in the scene.

**FPS: 355**

### 2. Image capture (high quality)

- `Images` data is sent per frame (`_img` pass only).
- The render quality is set to the highest possible setting.
- The images are compressed .jpg
- The images are 1024x1024.
- There are no objects in the scene.

**FPS: 42**

### 3. Kitchen benchmark

- There is a pre-defined procedurally-generated kitchen (the commands are loaded from a .json file)
- Requested output data per-frame:
  - `Transforms`
  - `DynamicCompositeObjects`
  - `Overlap` (for containment)

**FPS: 125**

## How to run TDW's main performance benchmark

1. If you haven't done so already, [clone the TDW repo](https://github.com/threedworld-mit/tdw)
2. `cd path/to/tdw/` (replace `path/to` with the actual path)
3. `git pull` to make sure that your local repo is up to date
4. `cd Python/benchmarking`
5. `python3 main.py`
6. If you haven't done so already, [download the latest release of TDW](https://github.com/threedworld-mit/tdw/releases/latest)
7. Extract the downloaded build
8. Run the build
9. Wait for the performance benchmark to complete (this might take up to five minutes).
10. Compare your results to those listed above

## How to benchmark your own controller

To benchmark your own controller, add a To benchmark your own code, add the [`Benchmark`](../python/add_ons/benchmark.md) add-on. In this example, we'll compare the frames per second (FPS) of sending commands without adding a camera to the scene vs. the FPS after adding a camera to the scene:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.benchmark import Benchmark

c = Controller()
b = Benchmark()
c.add_ons.append(b)
b.start()
for i in range(1000):
    c.communicate([])
b.stop()
print(b.fps)

commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 1.5, "z": 0}))
c.communicate(commands)
b.start()
for i in range(1000):
    c.communicate([])
b.stop()
print(b.fps)
c.communicate({"$type": "terminate"})
```

Output:

```
778.2112198643591
518.1101836971412
```

***

**Next: [Image capture](image_capture.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`Benchmark`](../python/add_ons/benchmark.md) 