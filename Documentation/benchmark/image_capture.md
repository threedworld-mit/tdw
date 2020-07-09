# Image Capture

These benchmarks measure the FPS of image capture in TDW. Image capture is unavoidably slow.

 To learn about alternative means of gathering observation data, read [this document](observation_data.md).

To learn about the controller used in these tests, read the [general benchmark document](benchmark.md).

These tests were performed on a Windows machine.

### Arguments

| Argument   | Description                                                  |
| ---------- | ------------------------------------------------------------ |
| `--boxes`  | Add 100 cube primitives to the scene.                        |
| `--images` | Create an avatar. Send `Images` data per frame.              |
| `--hi_res` | Set render quality to maximum. Enable shadows. Enable post-processing. Set screen size to 1024x1024. |
| `--passes` | Set the image passes to: `[_img]`, `[_id]`, or `[_img, _id]` |

### Results

| Test                                                   | FPS  |
| ------------------------------------------------------ | ---- |
| `--images --passes _img`                               | 300  |
| `--boxes --images --passes _id`                        | 223  |
| `--images --passes _img --hi_res`                      | 158  |
| `--images --passes _img --png`                         | 248  |
| `--images --passes _img --hi_res --size 1024`          | 41   |
| `--images --passes _id --hi_res --size 1024`           | 30   |
| `--images --passes _img_id --hi_res --size 1024`       | 15   |
| `--images --passes _img_id --hi_res --size 1024 --png` | 8    |

### How to run this test

```bash
cd <root>/Python/benchmarking
python3 image_capture.py
```

```bash
<run build>
```

