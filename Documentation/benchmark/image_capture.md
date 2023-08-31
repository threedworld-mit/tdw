##### Performance Benchmarks

# Image capture

These benchmarks measure the FPS of image capture and observation data in TDW. Image capture is unavoidably slow.

See [the Benchmark document](benchmark.md) for the test machine's system info.

## 1: Image capture

Performance benchmark for `Images` output data using different render settings:

| 100 objects | Pass masks        | Render quality | Post-processing | Screen size | .png  | FPS  |
| ----------- | ----------------- | -------------- | --------------- | ----------- | ----- | ---- |
| False       | `['_img']`        | 0              | False           | 256         | False | 312  |
| True        | `['_id']`         | 0              | False           | 256         | False | 400  |
| False       | `['_img']`        | 5              | True            | 256         | False | 234  |
| False       | `['_img']`        | 5              | True            | 1024        | False | 44   |
| True        | `['_id']`         | 0              | False           | 1024        | False | 69   |
| False       | `['_img']`        | 5              | True            | 1024        | True  | 41   |
| True        | `['_img', '_id']` | 5              | True            | 1024        | False | 33   |
| True        | `['_img', '_id']` | 5              | True            | 1024        | True  | 30   |

## 2. Observation data

Performance benchmark to compare `Images` data to alternative observation data. 

- Render quality is 0
- Post processing is disabled
- Screen size is 256x256
- Images are .jpg
- There are 100 objects in the scene
- Note that `Occlusion` is slow because it renders two images; it would normally require 2 frames to get the same data as `Occlusion`'s 1 frame.

| _img pass | _id pass | IdPassSegmentationColors | Occlusion | FPS  |
| --------- | -------- | ------------------------ | --------- | ---- |
| True      | False    | False                    | False     | 292  |
| False     | True     | False                    | False     | 350  |
| False     | False    | True                     | False     | 288  |
| False     | False    | False                    | True      | 196  |

## 3. Image capture (all)

This is a simple benchmark of all image passes.

- Render quality is 5
- Post processing is enabled
- Screen size is 256x256
- The `_img` pass is a .png
- There are 15 objects in the scene

**Result: 45 FPS**

## How to run TDW's image capture performance benchmarks

1. [Follow instructions in the Benchmark document for cloning the repo, downloading the build, etc.](benchmark.md)
2. `cd path/to/tdw/Python/benchmarking` (replace `path/to` with the actual path)
3. `python3 image_capture.py` or `python3 observation_data.py` or `python3 image_capture_all.py`
4. Run the build
5. Wait for the performance benchmark to complete (this might take up to five minutes).
6. Compare your results to those listed above


***

**Next: [Object data](object_data.md)**

[Return to the README](../../README.md)