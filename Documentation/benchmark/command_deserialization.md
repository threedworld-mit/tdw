# Command Deserialization

The build receives [commands](../api/command_api_guide.md) as JSON string and deserializes them into objects. This is an _innately slow process_, albeit highly optimized within TDW.

JSON is known to be slower than other serialization formats. However, on the backend, JSON allows us to rapidly iterate, fix, and create commands. Switching to a different serialization format would take a tremendous amount of time and result in a faster but much more fragile API; we've decided that this is not a good tradeoff.

## 1. To what extent does deserialization affect performance?

The test controller `do_nothing.py` sends increasing quantities of the command `{"$type": "do_nothing"}` for 1000 iterations. The build responds with an empty frame.

| Quantity | Size (bytes) | FPS |
| --- | --- | --- |
| 1 | 25 | 921 |
| 2 | 50 | 940 |
| 4 | 100 | 919 |
| 8 | 200 | 915 |
| 16 | 400 | 879 |
| 32 | 800 | 825 |
| 64 | 1600 | 780 |
| 128 | 3200 | 676 |
| 256 | 6400 | 578 |
| 512 | 12800 | 408 |
| 1024 | 25600 | 302 |
| 2048 | 51200 | 203 |

### How to run this test

```bash
cd <root>/Python/benchmarking
```

```bash
python3 do_nothing.py
```

## 2. How does the deserialization of structs affect performance?

The test controller `struct_deserialization.py` deserializing a Vector3 and a Quaternion per frame for 5000 frames. The build responds with an empty frame. 

The commands sent per frame are 163 bytes. This can be compared to `do_nothing.py`'s results (200 bytes) to gauge slowdown due to struct deserialization.

**Result: 621 FPS** _(Note: This was tested on a different machine than the do_nothing.py test; running the tests on the same machine resulted in 736 FPS for do_nothing.py at 200 bytes.)_

### How to run this test

```bash
cd <root>/Python/benchmarking
```

```bash
python3 struct_deserialization.py
```