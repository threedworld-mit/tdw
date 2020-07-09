# Machine Performance

We benchmark on three machines:

| Machine         | OS                 | CPU                            | Memory | GPU                                                          | Display  |
| --------------- | ------------------ | ------------------------------ | ------ | ------------------------------------------------------------ | -------- |
| `legion_lenovo` | Windows, Ubuntu 18 | 4.2 GHz 8 Cores                | 17 GB  | NVIDIA GeForce GTX 1080                                      | Yes      |
| `braintree`     | Ubuntu 16          | 1.218134839285714 GHz 56 Cores | 270 GB | NVIDIA  GeForce GTX TITAN Black , NVIDIA  GeForce GTX TITAN  | Headless |
| `node11`        | Ubuntu 16          | 1.606046875 GHz 16 Cores       | 135 GB | NVIDIA  TITAN X (Pascal) , NVIDIA  TITAN X (Pascal) , NVIDIA  TITAN X (Pascal) , NVIDIA  TITAN X (Pascal) | Headless |

### Comparison

- **`legion_lenovo` is substantially faster than either remote server.** The extent to which it is faster varies by [benchmark](benchmark.md) and machine, but it is on average approximately 30% faster. `braintree` is the slowest machine by a wide margin.
- **`legion_lenovo`, is _fastest_ when running Ubuntu 18.** Therefore, the remote servers aren't slow because they're running Linux.
- Ubuntu 16 is the same speed as Ubuntu 18.
- **The Linux machines _aren't_ slower when just sending object data.**  This implies that the slowdown is due to rendering.

## Sharing GPUs

The build will run slower if it has to share the GPU with another build or GPU-intensive process.

In the following tests, multiple build instances using the same GPU are launched. Only one of the builds is connected to a controller (in other words, all _n_ builds are rendering, but only 1 is returning data).

When running these tests, be sure to set each build to a different port, e.g.: `./TDW.x86_64 -port=1072`

### Legion-Lenovo (Ubuntu 18)

`benchmarker.py --images --passes _img`

| Number of build instances | FPS | Delta |
| --- | --- | --- |
| 1 | 386 | |
| 2 | 304 | -21% |
| 3 | 239 | - 21% |

`benchmarker.py --boxes --transforms`

| Number of build instances | FPS | Delta |
| --- | --- | --- |
| 1 | 850 | |
| 2 | 707 | -17% |
| 3 | 640 | - 16% |

### node11

`benchmarker.py --images --passes _img`

| Number of build instances | FPS | Delta |
| --- | --- | --- |
| 1 | ?\* | |
| 2 | 87 |  |
| 3 | 66 | -24% |

\* At the time this metrics were recorded, a build of TDW was running on every GPU on node11. These builds were almost certainly running slower than the benchmark test.