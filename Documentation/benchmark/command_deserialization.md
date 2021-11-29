##### Performance Benchmarks

# Command deserialization

The build receives commands as JSON string and deserializes them into objects. This process is highly optimized within TDW.

JSON is known to be slower than other serialization formats. However, on the backend, JSON allows us to rapidly iterate, fix, and create commands. Switching to a different serialization format would take a tremendous amount of time and result in a faster but much more fragile API; we've decided that this is not a good tradeoff.

## 1. Command deserialization performance benchmark

The test controller sends increasing quantities of the command `{"$type": "do_nothing"}` for 1000 iterations. The build responds with an empty frame.

| Quantity | Size (bytes) | FPS  |
| -------- | ------------ | ---- |
| 1        | 25           | 826  |
| 2        | 50           | 857  |
| 4        | 100          | 867  |
| 8        | 200          | 847  |
| 16       | 400          | 821  |
| 32       | 800          | 781  |
| 64       | 1600         | 717  |
| 128      | 3200         | 662  |
| 256      | 6400         | 611  |
| 512      | 12800        | 412  |
| 1024     | 25600        | 316  |
| 2048     | 51200        | 186  |

## 2. Struct deserialization

The test controller deserializes a Vector3 and a Quaternion per frame for 5000 frames. The build responds with an empty frame. 

**Result: 614 FPS**

## How to run TDW's deserialization performance benchmarks

1. [Follow instructions in the Benchmark document for cloning the repo, downloading the build, etc.](benchmark.md)
2. `cd path/to/tdw/Python/benchmarking` (replace `path/to` with the actual path)
3. `python3 command_deserialization.py` or `python3 struct_deserialization.py`
4. Run the build
5. Wait for the performance benchmark to complete (this might take up to five minutes).
6. Compare your results to those listed above

***

[Return to the README](../../../README.md)